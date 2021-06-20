from flask import Blueprint

from anubis.models import db, User, InCourse, Course
from anubis.utils.auth import require_user, current_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response, error_response
from anubis.utils.lms.assignments import get_assignments
from anubis.utils.lms.courses import valid_join_code, get_courses
from anubis.utils.services.cache import cache

courses_ = Blueprint("public-courses", __name__, url_prefix="/public/courses")


@courses_.route("/")
@courses_.route("/list")
@require_user()
@json_response
def public_classes():
    """
    Get class data for current user

    :return:
    """

    # Current user
    user: User = current_user()

    # Get the (possibly cached) courses
    # that the current user is in.
    courses = get_courses(user.netid)

    # Give back the courses that the
    # student is in. This information
    # is possibly cached.
    return success_response({
        "courses": courses
    })


@courses_.route("/join/<string:join_code>")
@require_user()
@json_response
def public_courses_join(join_code):
    """
    Get class data for current user

    :return:
    """
    user: User = current_user()

    # Validate that the join code contains valid characters
    if not valid_join_code(join_code):
        return error_response('Please give a valid join code')

    # Search courses for matching join code
    course = Course.query.filter(
        Course.join_code == join_code
    ).first()

    # If course not found, then we can hand back an error
    if course is None:
        return error_response("Join code is not valid :(")

    # Check to see if student is already in course
    in_course = InCourse.query.filter(
        InCourse.course_id == course.id,
        InCourse.owner_id == user.id,
    ).first()

    # If they are already in the course, then we can give them a warning
    if in_course is not None:
        return success_response({
            "status": "You are already in that class!",
            "variant": "warning",
        })

    # Create the new in-course
    in_course = InCourse(
        course_id=course.id,
        owner_id=user.id,
    )

    # Add and commit the course join entry
    db.session.add(in_course)
    db.session.commit()

    # Clear the cached entries for getting course data
    cache.delete_memoized(get_courses, user.netid)
    cache.delete_memoized(get_assignments, user.netid)
    cache.delete_memoized(get_assignments, user.netid, course.id)

    return success_response({
        "status": f"Joined {course.course_code}"
    })
