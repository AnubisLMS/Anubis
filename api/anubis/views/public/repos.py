from flask import Blueprint

from anubis.models import User
from anubis.utils.auth import current_user, require_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response
from anubis.utils.lms.repos import get_repos

repos = Blueprint("public-repos", __name__, url_prefix="/public/repos")


@repos.route("/")
@repos.route("/list")
@require_user()
@json_response
def public_repos():
    """
    Get all unique repos for a user

    :return:
    """
    user: User = current_user()

    _repos = get_repos(user.id)

    return success_response({"repos": _repos})
