import json

from flask import Blueprint, request

from anubis.models import Submission
from anubis.utils.cache import cache
from anubis.utils.decorators import json_response, load_from_id
from anubis.utils.auth import require_admin
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response
from anubis.utils.questions import get_assigned_questions
from anubis.utils.students import get_students, bulk_stats

stats = Blueprint("admin-stats", __name__, url_prefix="/admin/stats")


@stats.route("/assignment/<assignment_id>")
@stats.route("/assignment/<assignment_id>/<netid>")
@require_admin()
@log_endpoint("cli", lambda: "stats")
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
    netids = request.args.get("netids", None)
    force = request.args.get("force", False)

    if force is not False:
        cache.clear()

    if netids is not None:
        netids = json.loads(netids)
    elif netid is not None:
        netids = [netid]
    else:
        netids = list(map(lambda x: x["netid"], get_students()))

    bests = bulk_stats(assignment_id, netids)
    return success_response({"stats": bests})


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
                submission.assignment.id, submission.owner.id
            ),
            "class": submission.assignment.course.data,
        }
    )
