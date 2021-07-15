from flask import Blueprint, request

from anubis.utils.auth import current_user, require_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response
from anubis.utils.lms.assignments import get_assignments

assignments = Blueprint(
    "public-assignments", __name__, url_prefix="/public/assignments"
)


@assignments.route("/")
@assignments.route("/list")
@require_user()
@json_response
def public_assignments():
    """
    Get all the assignments for a user. Optionally specify a class
    name as a get query.

    /api/public/assignments?class=Intro to OS

    :return: { "assignments": [ assignment.data ] }
    """

    # Get optional class filter from get query
    course_id = request.args.get("courseId", default=None)

    # Get (possibly cached) assignment data
    assignment_data = get_assignments(current_user.netid, course_id)

    # Iterate over assignments, getting their data
    return success_response({"assignments": assignment_data})
