from typing import List

from flask import Blueprint

from anubis.models import User, AssignmentRepo, Assignment
from anubis.utils.auth import current_user, require_user
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response

repos = Blueprint("public-repos", __name__, url_prefix="/public/repos")


@repos.route("/")
@require_user()
@log_endpoint("repos", lambda: "repos")
@json_response
def public_repos():
    """
    Get all unique repos for a user

    :return:
    """
    user: User = current_user()

    repos: List[AssignmentRepo] = (
        AssignmentRepo.query.join(Assignment)
            .filter(AssignmentRepo.owner_id == user.id)
            .distinct(AssignmentRepo.repo_url)
            .order_by(Assignment.release_date.desc())
            .all()
    )

    return success_response({"repos": [repo.data for repo in repos]})
