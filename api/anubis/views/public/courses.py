import string

from flask import Blueprint

from anubis.models import db, User, InCourse, Course
from anubis.utils.assignment.assignments import get_courses
from anubis.utils.users.auth import require_user, current_user
from anubis.utils.http.decorators import json_response
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.http.https import success_response, error_response

courses = Blueprint("public-courses", __name__, url_prefix="/public/courses")


def valid_join_code(join_code: str) -> bool:
    """
    Validate code to make sure that all the characters are ok.

    :param join_code:
    :return:
    """

    # Create a valid charset from all ascii letters and numbers
    valid_chars = set(string.ascii_letters + string.digits)

    # Make sure the join code is 6 chars long, and
    # all the chars exist in the valid_chars set.
    return len(join_code) == 6 and all(c in valid_chars for c in join_code)


@courses.route("/")
@require_user()
@log_endpoint("public-classes")
@json_response
def public_classes():
    """
    Get class data for current user

    :return:
    """
    user: User = current_user()
    return success_response({"courses": get_courses(user.netid)})


@courses.route("/join/<string:join_code>")
@require_user()
@log_endpoint("join-course")
@json_response
def public_courses_join(join_code):
    """
    Get class data for current user

    :return:
    """
    user: User = current_user()

    if not valid_join_code(join_code):
        return error_response('Please give a valid join code')

    course = Course.query.filter(Course.id.like(join_code + "%")).first()

    if course is None:
        return error_response("Join code is not valid :(")

    in_course = InCourse.query.filter(
        InCourse.course_id == course.id,
        InCourse.owner_id == user.id,
    ).first()

    if in_course is not None:
        return success_response(
            {
                "status": "You are already in that class!",
            }
        )

    in_course = InCourse(
        course_id=course.id,
        owner_id=user.id,
    )

    db.session.add(in_course)
    db.session.commit()

    return success_response({"status": "Joined"})
