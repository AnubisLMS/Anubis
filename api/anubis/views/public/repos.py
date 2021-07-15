from flask import Blueprint

from anubis.models import User
from anubis.utils.auth import current_user, require_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response
from anubis.utils.lms.repos import get_repos

repos_ = Blueprint("public-repos", __name__, url_prefix="/public/repos")


@repos_.route("/")
@repos_.route("/list")
@require_user()
@json_response
def public_repos():
    """
    Get all unique repos for a user

    :return:
    """

    # Get all repos for the user
    repos = get_repos(current_user.id)

    # Pass them back
    return success_response({"repos": repos})
