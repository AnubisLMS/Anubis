from flask import Blueprint

from anubis.models import db, InCourse, Course
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http.decorators import json_response
from anubis.utils.http import error_response, success_response
from anubis.lms.assignments import get_assignments
from anubis.lms.courses import valid_join_code, get_courses
from anubis.utils.cache import cache

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

    # Get the (possibly cached) courses
    # that the current user is in.
    courses = get_courses(current_user.netid)

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

    # Validate that the join code contains valid characters
    if not valid_join_code(join_code):
        return error_response('Please give a valid join code')

    # Search courses for matching join code
    course = Course.query.filter(
        Course.join_code == join_code
    ).first()

    # If course not found, then we can hand back an error
    req_assert(course is not None, message='join code is not valid :(')

    # Check to see if student is already in course
    in_course = InCourse.query.filter(
        InCourse.course_id == course.id,
        InCourse.owner_id == current_user.id,
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
        owner_id=current_user.id,
    )

    # Add and commit the course join entry
    db.session.add(in_course)
    db.session.commit()

    # Clear the cached entries for getting course data
    cache.delete_memoized(get_courses, current_user.netid)
    cache.delete_memoized(get_assignments, current_user.netid)
    cache.delete_memoized(get_assignments, current_user.netid, course.id)

    return success_response({
        "status": f"Joined {course.course_code}"
    })
