from flask import Blueprint

from anubis.models import db, User, InCourse, Course
from anubis.utils.assignments import get_courses
from anubis.utils.auth import require_user, current_user
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response, error_response

courses = Blueprint("public-courses", __name__, url_prefix="/public/courses")


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

    if len(join_code) != 6:
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
