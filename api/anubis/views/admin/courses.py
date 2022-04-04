from flask import Blueprint
from sqlalchemy.exc import DataError, IntegrityError

from anubis.lms.courses import assert_course_superuser, course_context, valid_join_code
from anubis.models import Course, InCourse, ProfessorForCourse, TAForCourse, User, db
from anubis.utils.auth.http import require_admin, require_superuser
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert, row2dict
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_endpoint, json_response

courses_ = Blueprint("admin-courses", __name__, url_prefix="/admin/courses")


@courses_.route("/")
@courses_.route("/list")
@require_admin()
@json_response
def admin_courses_list():
    """
    list the data for the current course context.

    :return:
    """

    course_data = row2dict(course_context)
    if course_context.theia_default_image_id is not None:
        course_data["theia_default_image"] = course_context.theia_default_image.data
    else:
        course_data["theia_default_image"] = None

    # Return the course context broken down
    return success_response(
        {
            "course": course_data,
        }
    )


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
        professor_display_name="placeholder",
    )

    # Add it to the session
    db.session.add(course)

    # Commit the new Course
    db.session.commit()

    # Return the status
    return success_response(
        {
            "course": course.data,
            "status": "Created new course",
        }
    )


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
    db_course: Course = Course.query.filter(Course.id == course_id).first()

    # Make sure we got a course
    req_assert(db_course is not None, message="course not found")

    # Assert that the current user is a professor or a superuser
    assert_course_superuser(course_id)

    # Check that the join code is valid
    req_assert(
        valid_join_code(course["join_code"]),
        message="Invalid join code. Lowercase letters and numbers only.",
    )

    # Update all the items in the course with the posted data
    for column in Course.__table__.columns:
        if column.name in course:
            key, value = column.name, course[column.name]

            if isinstance(value, str):
                value = value.strip()

            if key == "theia_default_image_id":
                continue

            setattr(db_course, key, value)

    if course["theia_default_image"] is not None:
        db_course.theia_default_image_id = course["theia_default_image"]["id"]
    else:
        db_course.theia_default_image_id = None

    # Commit the changes
    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        return error_response("Unable to save " + str(e))

    # Return the status
    return success_response({"course": db_course.data, "status": "Changes saved."})


@courses_.route("/list/students")
@require_admin()
@json_response
def admin_course_list_students():
    """
    list all students for the current course context.

    :return:
    """

    # Get all the students in the current course context
    students = (
        User.query.join(InCourse)
            .filter(
            InCourse.course_id == course_context.id,
        )
            .all()
    )

    # Return the list of basic user information about the tas
    return success_response(
        {
            "users": [
                {
                    "id": user.id,
                    "netid": user.netid,
                    "name": user.name,
                    "github_username": user.github_username,
                }
                for user in students
            ]
        }
    )


@courses_.route("/list/tas")
@require_admin()
@json_response
def admin_course_list_tas():
    """
    list all TAs for the current course context.

    :return:
    """

    # Get all the TAs in the current course context
    tas = (
        User.query.join(TAForCourse)
            .filter(
            TAForCourse.course_id == course_context.id,
        )
            .all()
    )

    # Return the list of basic user information about the tas
    return success_response(
        {
            "users": [
                {
                    "id": user.id,
                    "netid": user.netid,
                    "name": user.name,
                    "github_username": user.github_username,
                }
                for user in tas
            ]
        }
    )


@courses_.route("/list/professors")
@require_admin()
@json_response
def admin_course_list_professors():
    """
    Get all the professors for the current course context.

    :return:
    """

    # Get all the professors within the current course context
    professors = (
        User.query.join(ProfessorForCourse)
            .filter(
            ProfessorForCourse.course_id == course_context.id,
        )
            .all()
    )

    # Return the list of basic user information about the professors
    return success_response(
        {
            "users": [
                {
                    "id": user.id,
                    "netid": user.netid,
                    "name": user.name,
                    "github_username": user.github_username,
                }
                for user in professors
            ]
        }
    )


@courses_.route("/make/student/<string:user_id>")
@require_admin()
@json_response
def admin_course_make_student_id(user_id: str):
    """
    Make a user a professor for a course

    :param user_id:
    :return:
    """

    # Get the other user
    other = User.query.filter(User.id == user_id).first()

    # Make sure they exist
    req_assert(other is not None, message="user does not exist")

    # Check to see if the other user is already a professor
    # for this course
    student = InCourse.query.filter(
        InCourse.owner_id == user_id,
        InCourse.course_id == course_context.id,
    ).first()

    # If they are already a professor, then stop
    req_assert(student is None, message="they are already a student")

    # Create a new professor
    student = InCourse(
        owner_id=user_id,
        course_id=course_context.id,
    )

    # Add and commit the change
    db.session.add(student)
    db.session.commit()

    # Return the status
    return success_response({"status": "Student added to course"})


@courses_.route("/remove/student/<string:user_id>")
@require_admin()
@json_response
def admin_course_remove_student_id(user_id: str):
    """
    Remove a professor from a course.

    :param user_id:
    :return:
    """

    # Get the other user
    other = User.query.filter(User.id == user_id).first()

    # Make sure the other user exists
    req_assert(other is not None, message="user does not exist")

    # Delete the professor
    InCourse.query.filter(
        InCourse.owner_id == user_id,
        InCourse.course_id == course_context.id,
    ).delete()

    # Commit the delete
    db.session.commit()

    # Return the status
    return success_response(
        {
            "status": "Student removed from course",
            "variant": "warning",
        }
    )


@courses_.route("/make/ta/<string:user_id>")
@require_admin()
@json_response
def admin_course_make_ta_id(user_id: str):
    """
    Make a user a ta for the current course.

    :param user_id:
    :return:
    """

    # Get the user that will be the TA
    other = User.query.filter(User.id == user_id).first()

    # Check that the user exists
    req_assert(other is not None, message="user does not exist")

    # Check to see if the user is already a ta
    ta = TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
        TAForCourse.course_id == course_context.id,
    ).first()

    # Check that they are not already a TA
    req_assert(ta is None, message="they are already a TA")

    # Make the user a TA if they are not already
    ta = TAForCourse(
        owner_id=user_id,
        course_id=course_context.id,
    )

    # Make sure they are in the course
    in_course = InCourse.query.filter(
        InCourse.course_id == course_context.id,
        InCourse.owner_id == current_user.id,
    ).first()
    if in_course is None:
        in_course = InCourse(course_id=course_context.id, owner_id=current_user.id)
        db.session.add(in_course)

    # Add and commit the change
    db.session.add(ta)
    db.session.commit()

    # Return the status
    return success_response({"status": "TA added to course"})


@courses_.route("/remove/ta/<string:user_id>")
@require_admin()
@json_response
def admin_course_remove_ta_id(user_id: str):
    """
    Remove a TA from the current course context

    :param user_id:
    :return:
    """

    # Assert that the current user is a professor or superuser
    assert_course_superuser(course_context.id)

    # Get the user object for the specified user
    other = User.query.filter(User.id == user_id).first()

    # Make sure that the other user exists
    req_assert(other is not None, message="user does not exist")

    # If the other user is the current user, then stop
    if not current_user.is_superuser:
        req_assert(other.id != current_user.id, message="cannot remove yourself")

    # Delete the TA
    TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
        TAForCourse.course_id == course_context.id,
    ).delete()

    # Commit the delete
    db.session.commit()

    # Return the status
    return success_response(
        {
            "status": "TA removed from course",
            "variant": "warning",
        }
    )


@courses_.route("/make/professor/<string:user_id>")
@require_superuser()
@json_response
def admin_course_make_professor_id(user_id: str):
    """
    Make a user a professor for a course

    :param user_id:
    :return:
    """

    # Get the other user
    other = User.query.filter(User.id == user_id).first()

    # Make sure they exist
    req_assert(other is not None, message="user does not exist")

    # Check to see if the other user is already a professor
    # for this course
    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
        ProfessorForCourse.course_id == course_context.id,
    ).first()

    # If they are already a professor, then stop
    req_assert(prof is None, message="they are already a professor")

    # Create a new professor
    prof = ProfessorForCourse(
        owner_id=user_id,
        course_id=course_context.id,
    )

    # Make sure they are in the course
    in_course = InCourse.query.filter(
        InCourse.course_id == course_context.id,
        InCourse.owner_id == current_user.id,
    ).first()
    if in_course is None:
        in_course = InCourse(course_id=course_context.id, owner_id=current_user.id)
        db.session.add(in_course)

    # Add and commit the change
    db.session.add(prof)
    db.session.commit()

    # Return the status
    return success_response({"status": "Professor added to course"})


@courses_.route("/remove/professor/<string:user_id>")
@require_superuser()
@json_response
def admin_course_remove_professor_id(user_id: str):
    """
    Remove a professor from a course.

    :param user_id:
    :return:
    """

    # Get the other user
    other = User.query.filter(User.id == user_id).first()

    # Make sure the other user exists
    req_assert(other is not None, message="user does not exist")

    # Delete the professor
    ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
        ProfessorForCourse.course_id == course_context.id,
    ).delete()

    # Commit the delete
    db.session.commit()

    # Return the status
    return success_response(
        {
            "status": "Professor removed from course",
            "variant": "warning",
        }
    )
