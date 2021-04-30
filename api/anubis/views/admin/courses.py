from flask import Blueprint
from sqlalchemy.exc import IntegrityError, DataError

from anubis.models import db, Course, TAForCourse, ProfessorForCourse, User
from anubis.utils.auth import require_admin, require_superuser, current_user
from anubis.utils.data import row2dict
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http.https import success_response, error_response
from anubis.utils.lms.course import assert_course_superuser, get_course_context

courses_ = Blueprint("admin-courses", __name__, url_prefix="/admin/courses")


@courses_.route("/")
@courses_.route("/list")
@require_admin()
@json_response
def admin_courses_list():
    """
    List the data for the current course context.

    :return:
    """

    # Get the course context
    course = get_course_context()

    # Return the course context broken down
    return success_response({
        "course": {"join_code": course.id[:6], **row2dict(course)},
    })


@courses_.route("/new")
@require_superuser()
@json_response
def admin_courses_new():
    """
    Create a new course will placeholder
    in all the fields.

    * Requires superuser *

    :return:
    """

    # Create a new course with placeholder
    # in all the fields.
    course = Course(
        name="placeholder",
        course_code="placeholder",
        section="a",
        professor="placeholder",
    )

    # Add it to the session
    db.session.add(course)

    # Commit the new Course
    db.session.commit()

    # Return the status
    return success_response({
        "course": course.data,
        "status": "Created new course",
    })


@courses_.route("/save", methods=["POST"])
@require_admin()
@json_endpoint(required_fields=[("course", dict)])
def admin_courses_save_id(course: dict):
    """
    Update information about the course.

    :param course:
    :return:
    """

    # Get the course id from the posted data
    course_id = course.get("id", None)

    # Try to get the database object corresponding to that course
    db_course = Course.query.filter(Course.id == course_id).first()

    # Make sure we got a course
    if db_course is None:
        return error_response("Course not found.")

    # Assert that the current user is a professor or a superuser
    assert_course_superuser(course_id)

    # Update all the items in the course with the posted data
    for column in Course.__table__.columns:
        if column.name in course:
            setattr(db_course, column.name, course[column.name])

    # Commit the changes
    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        return error_response("Unable to save " + str(e))

    # Return the status
    return success_response({"course": db_course.data, "status": "Changes saved."})


@courses_.route('/list/tas')
@require_admin()
@json_response
def admin_course_list_tas():
    """
    List all TAs for the current course context.

    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Get all the TAs in the current course context
    tas = User.query.join(TAForCourse).filter(
        TAForCourse.course_id == course.id,
    ).all()

    # Return the list of basic user information about the tas
    return success_response({'users': [
        {
            'id': user.id, 'netid': user.netid,
            'name': user.name, 'github_username': user.github_username
        }
        for user in tas
    ]})


@courses_.route('/list/professors')
@require_admin()
@json_response
def admin_course_list_professors():
    """
    Get all the professors for the current course context.

    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Get all the professors within the current course context
    professors = User.query.join(ProfessorForCourse).filter(
        ProfessorForCourse.course_id == course.id,
    ).all()

    # Return the list of basic user information about the professors
    return success_response({'users': [
        {
            'id': user.id, 'netid': user.netid,
            'name': user.name, 'github_username': user.github_username,
        }
        for user in professors
    ]})


@courses_.route('/make/ta/<string:user_id>')
@require_admin()
@json_response
def admin_course_make_ta_id(user_id: str):
    """
    Make a user a ta for the current course.

    :param user_id:
    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Get the user that will be the TA
    other = User.query.filter(User.id == user_id).first()

    # Check that the user exists
    if other is None:
        return error_response('User id does not exist')

    # Check to see if the user is already a ta
    ta = TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
    ).first()
    if ta is not None:
        return error_response('They are already a TA')

    # Make the user a TA if they are not already
    ta = TAForCourse(
        owner_id=user_id,
        course_id=course.id,
    )

    # Add and commit the change
    db.session.add(ta)
    db.session.commit()

    # Return the status
    return success_response({
        'status': 'TA added to course'
    })


@courses_.route('/remove/ta/<string:user_id>')
@require_admin()
@json_response
def admin_course_remove_ta_id(user_id: str):
    """
    Remove a TA from the current course context

    :param user_id:
    :return:
    """

    # Get the current user
    user = current_user()

    # Get the course context
    course = get_course_context()

    # Assert that the current user is a professor or superuser
    assert_course_superuser(course.id)

    # Get the user object for the specified user
    other = User.query.filter(User.id == user_id).first()

    # Make sure that the other user exists
    if other is None:
        return error_response('User id does not exist')

    # If the other user is the current user, then stop
    if not user.is_superuser and other.id == user.id:
        return error_response('cannot remove yourself')

    # Delete the TA
    TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
        TAForCourse.course_id == course.id,
    ).delete()

    # Commit the delete
    db.session.commit()

    # Return the status
    return success_response({
        'status': 'TA removed from course',
        'variant': 'warning',
    })


@courses_.route('/make/professor/<string:user_id>')
@require_superuser()
@json_response
def admin_course_make_professor_id(user_id: str):
    """
    Make a user a professor for a course

    :param user_id:
    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Get the other user
    other = User.query.filter(User.id == user_id).first()

    # Make sure they exist
    if other is None:
        return error_response('User id does not exist')

    # Check to see if the other user is already a professor
    # for this course
    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
    ).first()

    # If they are already a professor, then stop
    if prof is not None:
        return error_response('They are already a professor')

    # Create a new professor
    prof = ProfessorForCourse(
        owner_id=user_id,
        course_id=course.id,
    )

    # Add and commit the change
    db.session.add(prof)
    db.session.commit()

    # Return the status
    return success_response({
        'status': 'Professor added to course'
    })


@courses_.route('/remove/professor/<string:user_id>')
@require_superuser()
@json_response
def admin_course_remove_professor_id(user_id: str):
    """
    Remove a professor from a course.

    :param user_id:
    :return:
    """

    # Get the current user
    course = get_course_context()

    # Get the other user
    other = User.query.filter(User.id == user_id).first()

    # Make sure the other user exists
    if other is None:
        return error_response('User id does not exist')

    # Delete the professor
    ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
        ProfessorForCourse.course_id == course.id,
    ).delete()

    # Commit the delete
    db.session.commit()

    # Return the status
    return success_response({
        'status': 'Professor removed from course',
        'variant': 'warning',
    })
