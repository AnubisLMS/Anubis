import traceback
from datetime import datetime
from typing import Union, List, Dict, Tuple

from dateutil.parser import parse as date_parse, ParserError
from sqlalchemy import or_, and_

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
)
from anubis.utils.auth import get_user
from anubis.utils.lms.course import is_course_admin
from anubis.utils.services.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.services.logger import logger
from anubis.utils.lms.questions import ingest_questions
from anubis.utils.lms.course import assert_course_admin


@cache.memoize(timeout=5, unless=is_debug)
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


@cache.memoize(timeout=5, unless=is_debug)
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

    course_ids = []
    in_courses = InCourse.query.join(Course).filter(
        InCourse.owner_id == user.id,
    ).all()

    if course_id is not None:
        course_ids = [course_id]
    else:
        course_ids = [in_course.course.id for in_course in in_courses]

    assignments = []
    for course in course_ids:
        filters = []
        if not (user.is_superuser or is_course_admin(course_id)):
            filters.append(Assignment.release_date <= datetime.now())
            filters.append(Assignment.hidden == False)

        course_assignments = Assignment.query.join(Course).filter(
            Course.id == course,
            *filters,
        ).order_by(Assignment.due_date.desc()).all()
        assignments.extend(course_assignments)

    a = [a.data for a in assignments]
    for assignment_data in a:
        assignment_data["has_submission"] = (
                Submission.query.join(User)
                .join(Assignment)
                .filter(
                    Assignment.id == assignment_data["id"],
                    User.netid == netid,
                )
                .first()
                is not None
        )
        assignment_data["has_repo"] = (
                AssignmentRepo.query.filter(
                    AssignmentRepo.owner_id == user.id,
                    AssignmentRepo.assignment_id == assignment_data['id'],
                ).first()
                is not None
        )

    return a


@cache.memoize(timeout=3, unless=is_debug)
def get_submissions(
        user_id=None, course_id=None, assignment_id=None
) -> Union[List[Dict[str, str]], None]:
    """
    Get all submissions for a given netid. Cache the results. Optionally specify
    a class_name and / or assignment_name for additional filtering.

    :param user_id:
    :param course_id:
    :param assignment_id: id of assignment
    :return:
    """

    # Load user
    owner = User.query.filter(User.id == user_id).first()

    # Verify user exists
    if owner is None:
        return None

    # Build filters
    filters = []
    if course_id is not None and course_id != "":
        filters.append(Course.id == course_id)
    if user_id is not None and user_id != "":
        filters.append(User.id == user_id)
    if assignment_id is not None:
        filters.append(Assignment.id == assignment_id)

    submissions = (
        Submission.query.join(Assignment)
            .join(Course)
            .join(InCourse)
            .join(User)
            .filter(Submission.owner_id == owner.id, *filters)
            .all()
    )

    return [s.full_data for s in submissions]


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
    c: Course = Course.query.filter(
        or_(
            Course.name == course_name,
            Course.course_code == course_name,
        )
    ).first()
    if c is None:
        return "Unable to find class", False

    assert_course_admin(c.id)

    # Check if it exists
    if assignment is None:
        assignment = Assignment(
            theia_image=c.theia_default_image,
            theia_options=c.theia_default_options,
            unique_code=assignment_data["unique_code"],
            course=c,
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
            and_(
                AssignmentTest.assignment_id == assignment.id,
                AssignmentTest.name.notin_(assignment_data["tests"]),
            )
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
        assignment_test = (
            AssignmentTest.query.filter(
                Assignment.id == assignment.id,
                AssignmentTest.name == test_name,
            )
                .join(Assignment)
                .first()
        )

        # Create the assignment test if it did not already exist
        if assignment_test is None:
            assignment_test = AssignmentTest(assignment=assignment, name=test_name)
            db.session.add(assignment_test)

    # Sync the questions in the assignment data
    question_message = None
    if 'questions' in assignment_data:
        accepted, ignored, rejected = ingest_questions(
            assignment_data["questions"], assignment
        )
        question_message = {"accepted": accepted, "ignored": ignored, "rejected": rejected}

    db.session.commit()

    return {"assignment": assignment.data, "questions": question_message}, True
