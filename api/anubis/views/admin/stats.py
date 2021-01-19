import json

from flask import Blueprint, request

from anubis.models import Submission, Assignment, User
from anubis.utils.cache import cache
from anubis.utils.decorators import json_response, load_from_id
from anubis.utils.auth import require_admin
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response, get_number_arg
from anubis.utils.questions import get_assigned_questions
from anubis.utils.students import get_students
from anubis.utils.stats import bulk_stats, stats_for, stats_wrapper

stats = Blueprint("admin-stats", __name__, url_prefix="/admin/stats")


@stats.route("/assignment/<assignment_id>")
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

    bests = bulk_stats(assignment_id, limit=limit, offset=offset)
    return success_response({"stats": bests})


@stats.route("/for/<assignment_id>/<user_id>")
@require_admin()
@json_response
def private_stats_for(assignment_id, user_id):
    assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()
    user = User.query.filter(User.id == user_id).first()
    submission_id = stats_for(user_id, assignment_id)

    return success_response(
        {
            "stats": stats_wrapper(
                assignment, user.id, user.netid, user.name, submission_id
            )
        }
    )


@stats.route("/submission/<string:id>")
@require_admin()
@log_endpoint("cli", lambda: "submission-stats")
@load_from_id(Submission, verify_owner=False)
@json_response
def private_submission_stats_id(submission: Submission):
    """
    Get absolutely everything we have for specific submission.

    * This is can be a lot of data *

    :param submission:
    :return:
    """

    return success_response(
        {
            "student": submission.owner.data,
            "submission": submission.full_data,
            "assignment": submission.assignment.data,
            "questions": get_assigned_questions(
                submission.assignment.id, submission.owner.id, True
            ),
            "course": submission.assignment.course.data,
        }
    )
