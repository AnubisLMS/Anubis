from flask import Blueprint

from anubis.models import Submission, Assignment, User
from anubis.utils.auth import require_admin
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response, error_response, get_number_arg
from anubis.utils.lms.autograde import bulk_autograde, autograde, stats_wrapper
from anubis.utils.lms.questions import get_assigned_questions
from anubis.utils.services.elastic import log_endpoint

autograde_ = Blueprint("admin-autograde", __name__, url_prefix="/admin/autograde")


@autograde_.route("/assignment/<assignment_id>")
@require_admin()
@json_response
def private_stats_assignment(assignment_id, netid=None):
    """
    Calculate result statistics for an assignment. This endpoint is
    potentially very IO and computationally expensive. We basically
    need to load the entire submission history out of the database
    for the given assignment, then do calculations per user. For
    this reason, much of the individual computations here are quite
    heavily cached.

    * Due to how heavily cached the stats calculations are, once cached
    they will not be updated until there is a cache bust after the
    timeout. *

    :param assignment_id:
    :param netid:
    :return:
    """
    limit = get_number_arg("limit", 10)
    offset = get_number_arg("offset", 0)

    bests = bulk_autograde(assignment_id, limit=limit, offset=offset)
    return success_response({"stats": bests})


@autograde_.route("/for/<assignment_id>/<user_id>")
@require_admin()
@json_response
def private_stats_for(assignment_id, user_id):
    """TODO"""
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()
    user = User.query.filter(User.id == user_id).first()
    submission_id = autograde(user_id, assignment_id)

    return success_response(
        {
            "stats": stats_wrapper(
                assignment, user.id, user.netid, user.name, submission_id
            )
        }
    )


@autograde_.route("/submission/<string:assignment_id>/<string:netid>")
@require_admin()
@log_endpoint("cli", lambda: "submission-stats")
@json_response
def private_submission_stats_id(assignment_id: str, netid: str):
    """
    Get absolutely everything we have for specific submission.

    * This is can be a lot of data *

    :param assignment_id:
    :param netid:
    :return:
    """

    user = User.query.filter(
        User.netid == netid
    ).first()
    if user is None:
        return error_response('User does not exist')

    assignment = Assignment.query.filter(
        Assignment.id == assignment_id
    ).first()
    if assignment is None:
        return error_response('Assignment does not exist')

    submission_id = autograde(user.id, assignment.id)

    submission_full_data = None
    if submission_id is not None:
        submission = Submission.query.filter(
            Submission.id == submission_id
        ).first()
        submission_full_data = submission.admin_data

    return success_response(
        {
            "student": user.data,
            "submission": submission_full_data,
            "assignment": assignment.full_data,
            "questions": get_assigned_questions(
                assignment.id, user.id, True
            ),
            "course": assignment.course.data,
        }
    )
