from flask import Blueprint

from anubis.models import Assignment, User
from anubis.utils.auth import require_admin
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response, error_response
from anubis.utils.lms.courses import assert_course_context
from anubis.utils.visuals.assignments import (
    get_admin_assignment_visual_data,
    get_assignment_history,
    get_assignment_sundial,
)

visuals_ = Blueprint('admin-visuals', __name__, url_prefix='/admin/visuals')


@visuals_.route('/assignment/<string:assignment_id>')
@require_admin()
@json_response
def public_visuals_assignment_id(assignment_id: str):
    """
    Get the admin visual data for a specific assignment.

    Currently the data passed back feeds into the radial
    and passed time scatter graphs.

    :param assignment_id:
    :return:
    """

    # Get the assignment object
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id
    ).first()

    # If the assignment does not exist, then stop
    if assignment is None:
        return error_response('Assignment does not exist')

    # Assert that the assignment is within the course context
    assert_course_context(assignment)

    # Generate and pass back the visual data
    return success_response({
        'assignment_data': get_admin_assignment_visual_data(
            assignment_id
        )
    })


@visuals_.route('/history/<string:assignment_id>/<string:netid>')
@require_admin()
@json_response
def visual_history_assignment_netid(assignment_id: str, netid: str):
    """
    Get the visual history for a specific student and assignment.

    * lightly cached per assignment and user *

    :param assignment_id:
    :param netid:
    :return:
    """

    # Get the assignment object
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id
    ).first()

    # If the assignment does not exist, then stop
    if assignment is None:
        return error_response('Assignment does not exist')

    # Get the student
    student = User.query.filter(User.netid == netid).first()

    # Make sure that the student exists
    if student is None:
        return error_response('netid does not exist')

    # Assert that both the course and the assignment are
    # within the view of the current admin.
    assert_course_context(student, assignment)

    # Get tha cached assignment history
    return success_response(get_assignment_history(assignment.id, student.netid))


@visuals_.route('/sundial/<string:assignment_id>')
@require_admin()
@json_response
def visual_sundial_assignment(assignment_id: str):
    """
    Get the summary sundial data for an assignment. This endpoint
    is ridiculously IO intensive.

    * heavily cached *

    :param assignment_id:
    :return:
    """
    # Get the assignment object
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id
    ).first()

    # If the assignment does not exist, then stop
    if assignment is None:
        return error_response('Assignment does not exist')

    # Assert that the assignment is within the view of
    # the current admin.
    assert_course_context(assignment)

    # Pull the (maybe cached) sundial data
    return success_response({'sundial': get_assignment_sundial(assignment.id)})
