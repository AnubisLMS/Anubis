from typing import Optional

from dateutil.parser import parse as date_parse, ParserError
from flask import Blueprint

from anubis.models import db, LateException, Assignment, User
from anubis.utils.auth import require_admin
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http.https import success_response, error_response
from anubis.utils.lms.courses import assert_course_context
from anubis.utils.lms.submissions import recalculate_late_submissions

late_exceptions_ = Blueprint('admin-late-exceptions', __name__, url_prefix='/admin/late-exceptions')


@late_exceptions_.route('/list/<string:assignment_id>')
@require_admin()
@json_response
def admin_late_exception_list(assignment_id: str):
    """
    List all late exceptions for an assignment

    :param assignment_id:
    :return:
    """

    # Get the assignment
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    # Make sure it exists
    if assignment is None:
        return error_response('assignment does not exist')

    # Assert the course context
    assert_course_context(assignment)

    # Get late exceptions
    late_exceptions = LateException.query.filter(
        LateException.assignment_id == assignment.id
    ).all()

    # Break down for response
    return success_response({'assignment': assignment.full_data, 'late_exceptions': [
        late_exception.data
        for late_exception in late_exceptions
    ]})


@late_exceptions_.post('/update')
@require_admin()
@json_endpoint([('assignment_id', str), ('user_id', str), ('due_date', str)])
def admin_late_exception_update(assignment_id: str = None, user_id: str = None, due_date: str = None):
    """
    Add or update a late exception

    :param due_date:
    :param user_id:
    :param assignment_id:
    :return:
    """

    # Get the assignment and user
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()
    student = User.query.filter(User.id == user_id).first()

    # Make sure assignment and user exist
    if assignment is None:
        return error_response('assignment does not exist')
    if student is None:
        return error_response('user does not exist')

    assert_course_context(assignment, student)

    # Get late exceptions
    late_exception: Optional[LateException] = LateException.query.filter(
        LateException.assignment_id == assignment.id,
        LateException.user_id == student.id,
    ).first()
    if late_exception is None:
        late_exception = LateException(
            assignment_id=assignment.id,
            user_id=student.id,
        )
        db.session.add(late_exception)

    # Try to parse the datetime
    try:
        due_date = date_parse(due_date)
    except ParserError:
        return error_response('datetime could not be parsed')

    if due_date < assignment.due_date:
        return error_response('Exception cannot be before assignment due date')

    # Update the due date
    late_exception.due_date = due_date

    db.session.commit()

    # Recalculate the late submissions
    recalculate_late_submissions(student, assignment)

    # Break down for response
    return success_response({
        'status': 'Late exceptions updated'
    })


@late_exceptions_.route('/remove/<string:assignment_id>/<string:user_id>')
@require_admin()
@json_response
def admin_late_exception_remove(assignment_id: str = None, user_id: str = None):
    """
    Add or update a late exception

    :param user_id:
    :param assignment_id:
    :return:
    """

    # Get the assignment and user
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()
    student = User.query.filter(User.id == user_id).first()

    # Make sure assignment and user exist
    if assignment is None:
        return error_response('assignment does not exist')
    if student is None:
        return error_response('user does not exist')

    assert_course_context(assignment, student)

    # Delete the exception if it exists
    LateException.query.filter(
        LateException.assignment_id == assignment.id,
        LateException.user_id == student.id,
    ).delete()

    # Recalculate the late submissions
    recalculate_late_submissions(student, assignment)

    db.session.commit()

    # Break down for response
    return success_response({
        'status': 'Late exception deleted',
        'variant': 'warning',
    })
