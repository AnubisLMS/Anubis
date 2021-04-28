from flask import Blueprint

from anubis.models import db, User, Course, InCourse, Submission, Assignment
from anubis.utils.auth import require_admin, current_user, require_superuser
from anubis.utils.lms.course import get_course_context
from anubis.utils.services.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http.https import success_response, error_response, get_number_arg
from anubis.utils.lms.students import get_students
from anubis.utils.lms.course import assert_course_superuser

students = Blueprint("admin-students", __name__, url_prefix="/admin/students")


@students.route('/list/basic')
@require_admin()
@json_response
@cache.memoize(timeout=60, unless=is_debug)
def admin_student_list_basic():
    users = User.query.all()

    return success_response({
        'users': [
            {'id': user.id, 'netid': user.netid}
            for user in users
        ]
    })


@students.route("/list")
@require_admin()
@json_response
@cache.memoize(timeout=60, unless=is_debug)
def admin_students_list():
    course = get_course_context()

    return success_response({
        "students": get_students(course_id=course.id)
    })


@students.route("/info/<string:id>")
@require_admin()
@json_response
def admin_students_info_id(id: str):
    student = User.query.filter(
        User.id == id,
    ).first()

    course = get_course_context()

    # Check if student exists
    if student is None:
        return error_response("Student does not exist"), 400

    # Get courses student is in
    courses = Course.query.join(InCourse).filter(
        InCourse.owner_id == student.id,
        InCourse.course_id == course.id,
    ).all()

    return success_response({
        "student": student.data,
        "courses": [course.data for course in courses],
    })


@students.route("/submissions/<string:id>")
@require_admin()
@json_response
def admin_students_submissions_id(id: str):
    student = User.query.filter(
        User.id == id,
    ).first()

    course = get_course_context()

    # Check if student exists
    if student is None:
        return error_response("Student does not exist"), 400

    # Get an optional limit from the request query
    limit = get_number_arg("limit", 50)

    # Get n most recent submissions from the user
    submissions = (
        Submission.query.join(Assignment).filter(
            Submission.owner_id == student.id,
            Assignment.course_id == course.id,
        ).order_by(Submission.created.desc()).limit(limit).all()
    )

    return success_response({
        "student": student.data,
        "submissions": [submission.data for submission in submissions],
    })


@students.route("/update/<string:id>", methods=["POST"])
@require_admin()
@json_endpoint(
    required_fields=[("name", str), ("github_username", str)], only_required=True
)
def admin_students_update_id(id: str, name: str = None, github_username: str = None):
    user = current_user()
    student = User.query.filter(
        User.id == id,
    ).first()

    # Check if student exists
    if student is None:
        return error_response("Student does not exist"), 400

    if student.is_superuser and not user.is_superuser:
        return error_response('You cannot edit a superuser'), 400

    course = get_course_context()
    assert_course_superuser(course.id)

    incourse = InCourse.query.filter(
        InCourse.owner_id == student.id,
        InCourse.course_id == course.id,
    ).first()

    if incourse is None:
        return error_response('You cannot edit someone not in your course'), 400

    # Update fields
    student.name = name
    student.github_username = github_username

    # Commit changes
    db.session.add(student)
    db.session.commit()

    return success_response({
        "status": "saved",
    })


@students.route("/toggle-superuser/<string:id>")
@require_superuser()
@json_response
def admin_students_toggle_superuser(id: str):
    """
    Toggle the superuser status for a user. Requires user to be superuser
    to be able to make this change.

    :param id:
    :return:
    """
    user: User = current_user()
    other = User.query.filter(User.id == id).first()

    if not user.is_superuser:
        return error_response("Only superusers can create other superusers.")

    if other is None:
        return error_response("User could not be found")

    if user.id == other.id:
        return error_response("You can not toggle your own permission.")

    other.is_superuser = not other.is_superuser
    db.session.commit()

    if other.is_superuser:
        return success_response(
            {"status": f"{other.name} is now a superuser", "variant": "warning"}
        )

    else:
        return success_response(
            {"status": f"{other.name} is no longer a superuser", "variant": "success"}
        )
