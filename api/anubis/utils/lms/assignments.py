import traceback
from datetime import datetime
from typing import Union, List, Dict, Tuple, Optional

from dateutil.parser import parse as date_parse, ParserError
from sqlalchemy import or_

from anubis.models import (
    db,
    Course,
    InCourse,
    User,
    Assignment,
    Submission,
    AssignmentTest,
    AssignmentRepo,
    SubmissionTestResult,
    LateException,
)
from anubis.utils.auth import get_user
from anubis.utils.data import is_debug
from anubis.utils.lms.course import assert_course_admin
from anubis.utils.lms.course import is_course_admin
from anubis.utils.lms.questions import ingest_questions
from anubis.utils.services.cache import cache
from anubis.utils.services.logger import logger


@cache.memoize(timeout=60, unless=is_debug)
def get_courses(netid: str):
    """
    Get all classes a given netid is in

    :param netid:
    :return:
    """
    # Query for classes
    classes = Course.query.join(InCourse).join(User).filter(User.netid == netid).all()

    # Convert to list of data representation
    return [c.data for c in classes]


@cache.memoize(timeout=10, unless=is_debug, source_check=True)
def get_assignments(netid: str, course_id=None) -> Union[List[Dict[str, str]], None]:
    """
    Get all the current assignments for a netid. Optionally specify a class_name
    to filter by class.

    :param netid: netid of user
    :param course_id: optional class name
    :return: List[Assignment.data]
    """
    # Load user
    user = get_user(netid)

    # Verify user exists
    if user is None:
        return None

    # Get all the courses the user is in
    in_courses = InCourse.query.join(Course).filter(
        InCourse.owner_id == user.id,
    ).all()

    # Build a list of course ids. If the user
    # specified a specific course, make a list
    # of only that course id.
    course_ids = [course_id] \
        if course_id is not None \
        else [in_course.course.id for in_course in in_courses]

    # Build a list of all the assignments visible
    # to this user for each of the specified courses.
    assignments: List[Assignment] = []
    for _course_id in course_ids:
        # Query filters
        filters = []

        # If the current user is not a course admin or a superuser, then
        # we should filter out assignments that have not been released,
        # and those marked as hidden.
        if not is_course_admin(_course_id, user_id=user.id):
            filters.append(Assignment.release_date <= datetime.now())
            filters.append(Assignment.hidden == False)

        # Get the assignment objects that should be visible to this user.
        course_assignments = Assignment.query.join(Course).filter(
            Course.id == _course_id,
            *filters,
        ).all()

        # Add all the assignment objects to the running list
        assignments.extend(course_assignments)

    # Take all the sqlalchemy assignment objects,
    # and break them into data dictionaries.
    # Sort them by due_date.
    response = [_a.data for _a in sorted(
        assignments,
        reverse=True,
        key=lambda assignment: assignment.due_date,
    )]

    # Add submission and repo information to the assignments
    for assignment_data in response:
        # If the current user has a submission for this assignment, then mark it
        assignment_data["has_submission"] = (
                Submission.query.join(User).join(Assignment).filter(
                    Assignment.id == assignment_data["id"],
                    User.netid == netid,
                ).first() is not None
        )

        repo = AssignmentRepo.query.filter(
            AssignmentRepo.owner_id == user.id,
            AssignmentRepo.assignment_id == assignment_data['id'],
        ).first()

        # If the current user has a repo for this assignment, then mark it
        assignment_data["has_repo"] = (
                repo is not None
        )
        # If the current user has a repo for this assignment, then mark it
        assignment_data["repo_url"] = (
            repo.repo_url if repo is not None else None
        )

    return response


def assignment_sync(assignment_data: dict) -> Tuple[Union[dict, str], bool]:
    """
    Take an assignment_data dictionary from a assignment meta.yaml
    and update any and all existing data about the assignment.

    * This includes the assignment object fields, assignment tests,
    and assignment questions. *

    :param assignment_data:
    :return:
    """
    assignment = Assignment.query.filter(
        Assignment.unique_code == assignment_data["unique_code"]
    ).first()

    # Attempt to find the class
    course_name = assignment_data.get('class', None) or assignment_data.get('course', None)
    course: Course = Course.query.filter(
        or_(
            Course.name == course_name,
            Course.course_code == course_name,
        )
    ).first()
    if course is None:
        return "Unable to find class", False

    assert_course_admin(course.id)

    # Check if it exists
    if assignment is None:
        assignment = Assignment(
            theia_image=course.theia_default_image,
            theia_options=course.theia_default_options,
            unique_code=assignment_data["unique_code"],
            course=course,
        )

    # Update fields
    assignment.name = assignment_data["name"]
    assignment.hidden = assignment_data["hidden"]
    assignment.description = assignment_data["description"]
    assignment.pipeline_image = assignment_data["pipeline_image"]
    assignment.github_classroom_url = assignment_data["github_classroom_url"]
    try:
        assignment.release_date = date_parse(assignment_data["date"]["release"])
        assignment.due_date = date_parse(assignment_data["date"]["due"])
        assignment.grace_date = date_parse(assignment_data["date"]["grace"])
    except ParserError:
        logger.error(traceback.format_exc())
        return "Unable to parse datetime", 406

    db.session.add(assignment)

    # Go through assignment tests, and delete those that are now
    # not in the assignment data.
    for assignment_test in AssignmentTest.query.filter(
            AssignmentTest.assignment_id == assignment.id,
            AssignmentTest.name.notin_(assignment_data["tests"]),
    ).all():
        # Delete any and all submission test results that are still outstanding
        # for an assignment test that will be deleted.
        SubmissionTestResult.query.filter(
            SubmissionTestResult.assignment_test_id == assignment_test.id,
        ).delete()

        # Delete the assignment test
        AssignmentTest.query.filter(
            AssignmentTest.assignment_id == assignment.id,
            AssignmentTest.name == assignment_test.name,
        ).delete()

    # Run though the tests in the assignment data
    for test_name in assignment_data["tests"]:

        # Find if the assignment test exists
        assignment_test = AssignmentTest.query.join(Assignment).filter(
            Assignment.id == assignment.id,
            AssignmentTest.name == test_name,
        ).first()

        # Create the assignment test if it did not already exist
        if assignment_test is None:
            assignment_test = AssignmentTest(assignment=assignment, name=test_name)
            db.session.add(assignment_test)

    # Sync the questions in the assignment data
    question_message = None
    if 'questions' in assignment_data and isinstance(assignment_data['questions'], list):
        accepted, ignored, rejected = ingest_questions(
            assignment_data["questions"], assignment
        )
        question_message = {"accepted": accepted, "ignored": ignored, "rejected": rejected}

    db.session.commit()

    return {"assignment": assignment.data, "questions": question_message}, True


def get_assignment_due_date(user: Optional[User], assignment: Assignment) -> datetime:
    """
    Get the due date for an assignment for a specific user. We check to
    see if there is a late exception for this user, and return that if
    available. Otherwise, the default due date for the assignment is
    returned.

    :param user:
    :param assignment:
    :return:
    """

    if user is None:
        return assignment.due_date

    # Check for a late exception for this student
    late_exception: Optional[LateException] = LateException.query.filter(
        LateException.user_id == user.id,
        LateException.assignment_id == assignment.id,
    ).first()

    # If there was a late exception, return that due_date
    if late_exception is not None:
        return late_exception.due_date

    # If no late exception, return the assignment default
    return assignment.due_date
