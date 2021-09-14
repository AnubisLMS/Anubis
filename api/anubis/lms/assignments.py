import traceback
from datetime import datetime
from typing import Union, List, Dict, Tuple, Optional, Any

from dateutil.parser import parse as date_parse, ParserError
from sqlalchemy import or_

from anubis.models import (
    db,
    Course,
    User,
    Assignment,
    Submission,
    AssignmentTest,
    AssignmentRepo,
    SubmissionTestResult,
    LateException,
)
from anubis.utils.data import is_debug
from anubis.lms.courses import assert_course_admin, get_student_course_ids
from anubis.lms.courses import is_course_admin
from anubis.lms.questions import ingest_questions
from anubis.utils.cache import cache
from anubis.utils.logging import logger


@cache.memoize(timeout=30, unless=is_debug)
def get_assignment_grace(assignment_id: str) -> datetime:
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    return assignment.grace_date


@cache.memoize(timeout=30)
def get_assignment_due_date(user_id: str, assignment_id: str) -> datetime:
    """
    Get the due date for an assignment for a specific user. We check to
    see if there is a late exception for this user, and return that if
    available. Otherwise, the default due date for the assignment is
    returned.

    :param user_id:
    :param assignment_id:
    :return:
    """

    if user_id is None:
        return get_assignment_grace(assignment_id)

    # Check for a late exception for this student
    late_exception: Optional[LateException] = LateException.query.filter(
        LateException.user_id == user_id,
        LateException.assignment_id == assignment_id,
    ).first()

    # If there was a late exception, return that due_date
    if late_exception is not None:
        return late_exception.due_date

    # If no late exception, return the assignment default
    return get_assignment_grace(assignment_id)


@cache.memoize(timeout=30, unless=is_debug)
def get_assignment_data(user_id: str, assignment_id: str) -> Dict[str, Any]:
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    assignment_data = assignment.data
    fill_user_assignment_data(user_id, assignment_data)

    return assignment_data


@cache.memoize(timeout=10, unless=is_debug, source_check=True)
def get_assignments(netid: str, course_id=None) -> Optional[List[Dict[str, Any]]]:
    """
    Get all the current assignments for a netid. Optionally specify a class_name
    to filter by class.

    :param netid: netid of user
    :param course_id: optional class name
    :return: List[Assignment.data]
    """
    # Load user
    user = User.query.filter_by(netid=netid).first()

    # Verify user exists
    if user is None:
        return None

    # Get the list of course ids
    course_ids = get_student_course_ids(user, default=course_id)

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
        fill_user_assignment_data(user.id, assignment_data)

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
        return "Unable to find course", False

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
    assignment.github_template = assignment_data["github_template"]
    assignment.github_repo_required = assignment_data["github_repo_required"]
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

    # Commit changes
    db.session.commit()

    return {"assignment": assignment.data, "questions": question_message}, True


def fill_user_assignment_data(user_id: str, assignment_data: Dict[str, Any]):
    assignment_id: str = assignment_data['id']

    # If the current user has a submission for this assignment, then mark it
    assignment_data["has_submission"] = (
            Submission.query.filter(
                Submission.assignment_id == assignment_id,
                Submission.owner_id == user_id,
            ).count() > 0
    )

    repo = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == user_id,
        AssignmentRepo.assignment_id == assignment_id,
        AssignmentRepo.repo_created == True,
        AssignmentRepo.collaborator_configured == True,
    ).first()

    # If the current user has a repo for this assignment, then mark it
    assignment_data["has_repo"] = (
            repo is not None
    )
    # If the current user has a repo for this assignment, then mark it
    assignment_data["repo_url"] = (
        repo.repo_url if repo is not None else None
    )

    due_date = get_assignment_due_date(user_id, assignment_id)
    assignment_data['past_due'] = due_date < datetime.now()
    assignment_data['due_date'] = str(due_date)