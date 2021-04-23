import string
from datetime import timedelta, datetime

from flask import Blueprint, request

from anubis.models import User, db
from anubis.utils.users.auth import current_user, require_user
from anubis.utils.decorators import json_response
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.http.https import error_response, success_response
from anubis.utils.services.logger import logger

profile = Blueprint("public-profile", __name__, url_prefix="/public/profile")


@profile.route("/set-github-username")
@require_user()
@log_endpoint("public-set-github-username", lambda: "github username set")
@json_response
def public_set_github_username():
    u: User = current_user()

    github_username = request.args.get("github_username", default=None)
    if github_username is None:
        return error_response("missing field")
    github_username = github_username.strip()

    if any(i in string.whitespace for i in github_username):
        return error_response("Your username can not have spaces")

    if not (
            all(i in (string.ascii_letters + string.digits + "-") for i in github_username)
            and not github_username.startswith("-")
            and not github_username.endswith("-")
    ):
        return error_response(
            "Github usernames may only contain alphanumeric characters "
            "or single hyphens, and cannot begin or end with a hyphen."
        )

    logger.info(str(u.last_updated))
    logger.info(str(u.last_updated + timedelta(hours=1)) + " - " + str(datetime.now()))

    if (
            u.github_username is not None
            and u.last_updated + timedelta(hours=1) < datetime.now()
    ):
        return error_response(
            "Github usernames can only be "
            "changed one hour after first setting. "
            "Email the TAs to reset your github username."
        )  # reject their github username change

    u.github_username = github_username
    db.session.add(u)
    db.session.commit()

    return success_response(github_username)
