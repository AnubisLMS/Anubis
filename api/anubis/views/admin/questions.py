from flask import Blueprint

from anubis.models import Assignment
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import error_response, success_response
from anubis.utils.questions import hard_reset_questions, get_all_questions, assign_questions

questions = Blueprint('admin-questions', __name__, url_prefix='/admin-questions')


@questions.route('/hard-reset/<string:unique_code>')
@log_endpoint('cli', lambda: 'question hard reset')
@json_response
def private_questions_hard_reset_unique_code(unique_code: str):
    """
    This endpoint should be used very sparingly. When this is hit,
    assuming the assignment exists, it will delete all questions
    for the given assignment. This is potentially very destructive,
    because you will not be able to get the question assignments
    back without a database backup.

    * If you chose to use this half way into an assignment without
    being able to reset, you will need to assign new questions to
    students! *

    If you end up needing to re-assign questions, this has the
    potential to create a great deal of confusion among students.

    ** Be careful with this one **

    :param unique_code:
    :return:
    """
    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response('Unable to find assignment')

    # Hard reset questions
    hard_reset_questions(assignment)

    return success_response({
        'status': 'questions deleted'
    })


@questions.route('/get/<string:unique_code>')
@log_endpoint('cli', lambda: 'questions get')
@json_response
def private_questions_get_unique_code(unique_code: str):
    """
    Get all questions for the given assignment.

    :param unique_code:
    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response('Unable to find assignment')

    return get_all_questions(assignment)


@questions.route('/assign/<string:unique_code>')
@log_endpoint('cli', lambda: 'question assign')
@json_response
def private_questions_assign_unique_code(unique_code: str):
    """
    Assign questions that have been created. This action will only run once.
    Once a question is assigned to a student, the only way to change it is
    by manually editing the database. This is by design to reduce confusion.

    Questions must already be created to use this.

    :return:
    """

    # Try to find assignment
    assignment: Assignment = Assignment.query.filter(
        Assignment.unique_code == unique_code
    ).first()
    if assignment is None:
        return error_response('Unable to find assignment')

    # Assign the questions
    assigned_questions = assign_questions(assignment)

    # Pass back the response
    return success_response({'assigned': assigned_questions})
