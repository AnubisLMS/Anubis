from flask import Blueprint

from anubis.utils.auth import require_admin
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response
from anubis.utils.visuals.assignments import get_assignment_visual_data

visuals_ = Blueprint('admin-visuals', __name__, url_prefix='/admin/visuals')


@visuals_.route('/assignment/<string:assignment_id>')
@require_admin()
@json_response
def public_visuals_assignment_id(assignment_id: str):
    """TODO"""
    return success_response({
        'assignment_data': get_assignment_visual_data(
            assignment_id
        )
    })
