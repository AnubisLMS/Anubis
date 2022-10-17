from flask import Blueprint

from anubis.lms.submissions import init_submission
from anubis.models import Submission
from anubis.utils.auth.http import require_superuser
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response

dangling = Blueprint("admin-dangling", __name__, url_prefix="/admin/dangling")


@dangling.route("/list")
@require_superuser()
@json_response
def private_dangling():
    """
    This route should hand back a json list of all submissions that are dangling.
    Dangling being that we have no netid to match to the github username that
    submitted the assignment.

    :return:
    """

    # Pull all the dandling submissions
    dangling_ = Submission.query.filter(
        Submission.owner_id == None,
    ).all()

    # Get the data response for the dangling submissions
    dangling_ = [a.data for a in dangling_]

    # Pass back all the dangling submissions
    return success_response({"count": len(dangling_), "dangling": dangling_})


@dangling.route("/reset")
@require_superuser()
@json_response
def private_reset_dangling():
    """
    Reset all the submission that are dangling

    :return:
    """

    # Build a list of all the reset submissions
    resets = []

    # Iterate over all the dangling submissions
    for submission in Submission.query.filter_by(owner_id=None).all():
        # Reset the submission models
        init_submission(submission)

        # Append the new dangling submission data for the response
        resets.append(submission.data)

    # Return all the reset submissions
    return success_response({"reset": resets})

