from typing import List

from flask import Blueprint

from anubis.lms.courses import assert_course_context, assert_course_superuser, course_context
from anubis.lms.repos import get_repos
from anubis.lms.students import get_students
from anubis.lms.theia import get_recent_sessions
from anubis.models import Assignment, Course, InCourse, Submission, User, db
from anubis.utils.auth.http import require_admin, require_superuser
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http import get_number_arg, success_response
from anubis.utils.http.decorators import json_endpoint, json_response

students_ = Blueprint("admin-students", __name__, url_prefix="/admin/students")


@students_.route("/list/basic")
@require_admin()
@json_response
def admin_student_list_basic():
    """
    List the most basic information about all the students
    within the Anubis system.

    :return:
    """

    # Get all users
    students: List[User] = User.query.all()

    # Return their id and netid
    return success_response({"users": [{"id": user.id, "netid": user.netid, "name": user.name} for user in students]})


@students_.route("/list")
@require_admin()
@json_response
def admin_students_list():
    """
    List all users within the current course context

    :return:
    """

    # Get all students within the current course context
    students = get_students(course_context.id)

    # Pass back the students
    return success_response({"students": students})


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
    req_assert(student is not None, message="student does not exist")

    # Assert that the student is within the current course context
    assert_course_context(student)

    # Get courses student is in
    in_courses = InCourse.query.filter(
        InCourse.owner_id == student.id,
    ).all()

    # Get a list of all the course ids
    course_ids = list(map(lambda x: x.course_id, in_courses))

    # Get the course objects
    courses = Course.query.filter(Course.id.in_(course_ids)).all()

    repos = get_repos(student.id)
    recent_theia = get_recent_sessions(student.id)

    # Pass back the student and course information
    return success_response(
        {
            "user": student.data,
            "courses": [course.data for course in courses],
            "repos": repos,
            "theia": recent_theia,
        }
    )


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

    # Get the user object
    student = User.query.filter(User.id == id).first()

    # Check if student exists
    req_assert(student is not None, message="student does not exist")

    # Get n most recent submissions from the user
    submissions = (
        Submission.query.join(Assignment)
            .filter(
            Submission.owner_id == student.id,
            Assignment.course_id == course_context.id,
        )
            .order_by(Submission.created.desc())
            .limit(limit)
            .offset(offset)
            .all()
    )

    # Pass back the student and submission information
    return success_response(
        {
            "student": student.data,
            "submissions": [submission.data for submission in submissions],
        }
    )


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

    # Assert that the current user is a professor
    # or superuser in the course context
    assert_course_superuser(course_context.id)

    # Get the current user
    user = current_user

    # Get the student object
    student = User.query.filter(User.id == id).first()

    # Check if student exists
    req_assert(student is not None, message="student does not exist")

    # If the student is a superuser, then stop
    req_assert(
        not (student.is_superuser and not user.is_superuser),
        message="cannot edit a superuser",
    )

    # Make sure that the student is within the course context
    in_course = InCourse.query.filter(
        InCourse.owner_id == student.id,
        InCourse.course_id == course_context.id,
    ).first()

    # Verify that the student is in the context
    req_assert(in_course is not None, message="cannot edit outside your course context")

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

    # Get the other user
    other = User.query.filter(User.id == id).first()

    # Double check that the current user is a superuser
    req_assert(current_user.is_superuser, message="only superusers can create superusers")

    # If the other user was not found, then stop
    req_assert(other is not None, message="user does not exist")

    # Make sure that the other user is not also the current user
    req_assert(current_user.id != other.id, message="cannot toggle your own superuser")

    # Toggle the superuser field
    other.is_superuser = not other.is_superuser

    # Commit the change
    db.session.commit()

    # Pass back the status based on if the other is now a superuser
    if other.is_superuser:
        return success_response({"status": f"{other.name} is now a superuser", "variant": "warning"})

    # Pass back the status based on if the other user is now no longer a superuser
    else:
        return success_response({"status": f"{other.name} is no longer a superuser", "variant": "success"})
