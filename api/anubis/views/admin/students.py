from flask import Blueprint

from anubis.models import db, User, Course, InCourse, Submission, Assignment
from anubis.utils.auth import require_admin, current_user, require_superuser
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http.https import success_response, error_response, get_number_arg
from anubis.utils.lms.courses import assert_course_superuser, get_course_context, assert_course_context
from anubis.utils.lms.repos import get_repos
from anubis.utils.lms.students import get_students
from anubis.utils.lms.theia import get_recent_sessions

students_ = Blueprint("admin-students", __name__, url_prefix="/admin/students")


@students_.route('/list/basic')
@require_admin()
@json_response
def admin_student_list_basic():
    """
    List the most basic information about all the students
    within the Anubis system.

    :return:
    """

    # Get all users
    students = get_students()

    # Return their id and netid
    return success_response({
        'users': [
            {'id': user['id'], 'netid': user['netid']}
            for user in students
        ]
    })


@students_.route("/list")
@require_admin()
@json_response
def admin_students_list():
    """
    List all users within the current course context

    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Get all students within the current course context
    students = get_students(course_id=course.id)

    # Pass back the students
    return success_response({
        "students": students
    })


@students_.route("/info/<string:id>")
@require_admin()
@json_response
def admin_students_info_id(id: str):
    """
    Get basic information about a specific student by id.

    :param id:
    :return:
    """

    # Get the student object
    student = User.query.filter(
        User.id == id,
    ).first()

    # Check if student exists
    if student is None:
        return error_response("Student does not exist")

    assert_course_context(student)

    # Get courses student is in
    in_courses = InCourse.query.filter(
        InCourse.owner_id == student.id,
    ).all()

    # Get a list of all the course ids
    course_ids = list(map(lambda x: x.course_id, in_courses))

    # Get the course objects
    courses = Course.query.filter(
        Course.id.in_(course_ids)
    ).all()

    repos = get_repos(student.id)
    recent_theia = get_recent_sessions(student.id)

    # Pass back the student and course information
    return success_response({
        "user": student.data,
        "courses": [course.data for course in courses],
        "repos": repos,
        "theia": recent_theia,
    })


@students_.route("/submissions/<string:id>")
@require_admin()
@json_response
def admin_students_submissions_id(id: str):
    """
    Get some number of submissions for a specific user within
    the course context.

    use limit and offset parameters to view submission window

    :param id:
    :return:
    """

    # Get an optional limit and offset for query
    limit = get_number_arg("limit", 50)
    offset = get_number_arg("offset", 0)

    # Get the current course context
    course = get_course_context()

    # Get the user object
    student = User.query.filter(User.id == id).first()

    # Check if student exists
    if student is None:
        return error_response("Student does not exist")

    # Get n most recent submissions from the user
    submissions = (
        Submission.query.join(Assignment).filter(
            Submission.owner_id == student.id,
            Assignment.course_id == course.id,
        ).order_by(Submission.created.desc()).limit(limit).offset(offset).all()
    )

    # Pass back the student and submission information
    return success_response({
        "student": student.data,
        "submissions": [submission.data for submission in submissions],
    })


@students_.route("/update/<string:id>", methods=["POST"])
@require_admin()
@json_endpoint([("name", str), ("github_username", str)], only_required=True)
def admin_students_update_id(id: str, name: str = None, github_username: str = None):
    """
    Update either the name of github username of a student.

    The student must be within the current course context, and the
    user making the change must be a professor or superuser.

    :param id:
    :param name:
    :param github_username:
    :return:
    """

    # Get the course context
    course = get_course_context()

    # Assert that the current user is a professor
    # or superuser in the course context
    assert_course_superuser(course.id)

    # Get the current user
    user = current_user()

    # Get the student object
    student = User.query.filter(User.id == id).first()

    # Check if student exists
    if student is None:
        return error_response("Student does not exist")

    # If the student is a superuser, then stop
    if student.is_superuser and not user.is_superuser:
        return error_response('You cannot edit a superuser')

    # Make sure that the student is within the course context
    in_course = InCourse.query.filter(
        InCourse.owner_id == student.id,
        InCourse.course_id == course.id,
    ).first()

    # Verify that the student is in the context
    if in_course is None:
        return error_response('You cannot edit someone not in your course')

    # Update fields
    student.name = name
    student.github_username = github_username

    # Commit changes
    db.session.add(student)
    db.session.commit()

    # Pass back the status
    return success_response({"status": "saved"})


@students_.route("/toggle-superuser/<string:id>")
@require_superuser()
@json_response
def admin_students_toggle_superuser(id: str):
    """
    Toggle the superuser status for a user. Requires user to be superuser
    to be able to make this change.

    :param id:
    :return:
    """

    # Get the current user
    user = current_user()

    # Get the other user
    other = User.query.filter(User.id == id).first()

    # Double check that the current user is a superuser
    if not user.is_superuser:
        return error_response("Only superusers can create other superusers.")

    # If the other user was not found, then stop
    if other is None:
        return error_response("User could not be found")

    # Make sure that the other user is not also the current user
    if user.id == other.id:
        return error_response("You can not toggle your own permission.")

    # Toggle the superuser field
    other.is_superuser = not other.is_superuser

    # Commit the change
    db.session.commit()

    # Pass back the status based on if the other is now a superuser
    if other.is_superuser:
        return success_response({
            "status": f"{other.name} is now a superuser", "variant": "warning"
        })

    # Pass back the status based on if the other user is now no longer a superuser
    else:
        return success_response({
            "status": f"{other.name} is no longer a superuser", "variant": "success"
        })
