from flask import Blueprint

from anubis.models import db, User, Course, InCourse, Submission
from anubis.utils.auth import require_admin
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.decorators import json_response, json_endpoint
from anubis.utils.http import success_response, error_response, get_number_arg
from anubis.utils.students import get_students

students = Blueprint('admin-students', __name__, url_prefix='/admin/students')


@students.route('/list')
@require_admin
@json_response
@cache.cached(timeout=5, unless=is_debug)
def admin_students_list():
    return success_response({
        'students': get_students()
    })


@students.route('/info/<string:id>')
@require_admin
@json_response
def admin_students_info_id(id: str):
    student = User.query.filter(
        User.id == id,
    ).first()

    # Check if student exists
    if student is None:
        return error_response('Student does not exist'), 400

    # Get courses student is in
    courses = Course.query.join(InCourse).filter(
        InCourse.owner_id == student.id,
    ).all()

    return success_response({
        'student': student.data,
        'courses': [course.data for course in courses],
    })


@students.route('/submissions/<string:id>')
@require_admin
@json_response
def admin_students_submissions_id(id: str):
    student = User.query.filter(
        User.id == id,
    ).first()

    # Check if student exists
    if student is None:
        return error_response('Student does not exist'), 400

    # Get an optional limit from the request query
    limit = get_number_arg('limit', 50)

    # Get n most recent submissions from the user
    submissions = Submission.query.filter(
        Submission.owner_id == student.id,
    ).orderby(Submission.created.desc()).limit(limit).all()

    return success_response({
        'student': student.data,
        'submissions': [submission.data for submission in submissions]
    })


@students.route('/update/<string:id>', methods=['POST'])
@require_admin
@json_endpoint(required_fields=[('name', str), ('github_username', str)], only_required=True)
def admin_students_update_id(id: str, name: str = None, github_username: str = None):
    student = User.query.filter(
        User.id == id,
    ).first()

    # Check if student exists
    if student is None:
        return error_response('Student does not exist'), 400

    # Update fields
    student.name = name
    student.github_username = github_username

    # Commit changes
    db.session.add(student)
    db.session.commit()

    return success_response({
        'status': 'saved',
    })
