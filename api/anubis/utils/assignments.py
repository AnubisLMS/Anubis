import traceback
from datetime import datetime
from typing import Union, List, Dict

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
)
from anubis.utils.auth import get_user
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.logger import logger
from anubis.utils.questions import ingest_questions


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


@cache.memoize(timeout=60, unless=is_debug)
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

    filters = []
    if course_id is not None:
        filters.append(Course.id == course_id)

    assignments = (
        Assignment.query.join(Course)
            .join(InCourse)
            .join(User)
            .filter(
            User.netid == netid,
            Assignment.hidden == False,
            Assignment.release_date <= datetime.now(),
            *filters
        )
            .order_by(Assignment.due_date.desc())
            .all()
    )

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
    owner = User.query.filter(
        User.id == user_id
    ).first()

    # Verify user exists
    if owner is None:
        return None

    # Build filters
    filters = []
    if course_id is not None and course_id != '':
        filters.append(Course.id == course_id)
    if user_id is not None and user_id != '':
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


def assignment_sync(assignment_data):
    assignment = Assignment.query.filter(
        Assignment.unique_code == assignment_data["unique_code"]
    ).first()

    # Attempt to find the class
    c = Course.query.filter(
        or_(
            Course.name == assignment_data["class"],
            Course.course_code == assignment_data["class"],
        )
    ).first()
    if c is None:
        return "Unable to find class", False

    # Check if it exists
    if assignment is None:
        assignment = Assignment(unique_code=assignment_data["unique_code"])

    # Update fields
    assignment.name = assignment_data["name"]
    assignment.hidden = assignment_data["hidden"]
    assignment.description = assignment_data["description"]
    assignment.pipeline_image = assignment_data["pipeline_image"]
    assignment.github_classroom_url = assignment_data["github_classroom_url"]
    assignment.course = c
    try:
        assignment.release_date = date_parse(assignment_data["date"]["release"])
        assignment.due_date = date_parse(assignment_data["date"]["due"])
        assignment.grace_date = date_parse(assignment_data["date"]["grace"])
    except ParserError:
        logger.error(traceback.format_exc())
        return "Unable to parse datetime", 406

    db.session.add(assignment)
    db.session.commit()

    for i in AssignmentTest.query.filter(
            and_(
                AssignmentTest.assignment_id == assignment.id,
                AssignmentTest.name.notin_(assignment_data["tests"]),
            )
    ).all():
        db.session.delete(i)
    db.session.commit()

    for test_name in assignment_data["tests"]:
        assignment_test = (
            AssignmentTest.query.filter(
                Assignment.id == assignment.id,
                AssignmentTest.name == test_name,
            )
                .join(Assignment)
                .first()
        )

        if assignment_test is None:
            assignment_test = AssignmentTest(assignment=assignment, name=test_name)
            db.session.add(assignment_test)
            db.session.commit()

    accepted, ignored, rejected = ingest_questions(
        assignment_data["questions"], assignment
    )
    question_message = {"accepted": accepted, "ignored": ignored, "rejected": rejected}

    return {"assignment": assignment.data, "questions": question_message}, True
