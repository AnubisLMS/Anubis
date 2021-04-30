from flask import Blueprint

from anubis.models import Assignment
from anubis.utils.auth import require_admin
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response, error_response
from anubis.utils.visuals.assignments import get_admin_assignment_visual_data
from anubis.utils.lms.course import get_course_context, assert_course_context, assert_course_admin

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
