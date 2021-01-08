from flask import Blueprint, request

from anubis.models import User, Assignment, AssignedStudentQuestion, db
from anubis.utils.assignments import get_classes, get_assignments
from anubis.utils.auth import current_user, require_user
from anubis.utils.decorators import json_response, load_from_id, json_endpoint
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import get_request_ip, success_response
from anubis.utils.questions import get_assigned_questions

assignments = Blueprint('public-assignments', __name__, url_prefix='/public/assignments')


@assignments.route('/classes')
@require_user
@log_endpoint('public-classes', lambda: 'get classes {}'.format(get_request_ip()))
@json_response
def public_classes():
    """
    Get class data for current user

    :return:
    """
    user: User = current_user()
    return success_response({
        'classes': get_classes(user.netid)
    })


@assignments.route('/')
@require_user
@log_endpoint('public-assignments', lambda: 'get assignments {}'.format(get_request_ip()))
@json_response
def public_assignments():
    """
    Get all the assignments for a user. Optionally specify a class
    name as a get query.

    /api/public/assignments?class=Intro to OS

    :return: { "assignments": [ assignment.data ] }
    """

    # Get optional class filter from get query
    class_name = request.args.get('class', default=None)

    # Load current user
    user: User = current_user()

    # Get (possibly cached) assignment data
    assignment_data = get_assignments(user.netid, class_name)

    # Iterate over assignments, getting their data
    return success_response({
        'assignments': assignment_data
    })


@assignments.route('/questions/get/<int:id>')
@require_user
@log_endpoint('public-questions-get', lambda: 'get questions')
@load_from_id(Assignment, verify_owner=False)
@json_response
def public_assignment_questions_id(assignment: Assignment):
    """
    Get assigned questions for the current user for a given assignment.

    :param assignment:
    :return:
    """
    # Load current user
    user: User = current_user()

    return success_response({
        'questions': get_assigned_questions(assignment.id, user.id)
    })


@assignments.route('/questions/save/<int:id>')
@require_user
@log_endpoint('public-questions-save', lambda: 'save questions')
@load_from_id(AssignedStudentQuestion, verify_owner=True)
@json_endpoint(required_fields=[('response', str)])
def public_assignment_questions_save_id(assigned_question: AssignedStudentQuestion, response: str, **kwargs):
    """
    Save response for a given assignment question

    :param assigned_question:
    :param response:
    :param kwargs:
    :return:
    """
    assigned_question.response = response

    db.session.add(assigned_question)
    db.session.commit()

    return success_response('Success')
