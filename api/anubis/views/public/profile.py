import string

from flask import Blueprint, request

from anubis.models import User, db
from anubis.utils.auth import current_user, require_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import error_response, success_response
from anubis.utils.services.elastic import log_endpoint

profile = Blueprint("public-profile", __name__, url_prefix="/public/profile")


@profile.route("/set-github-username")
@require_user()
@log_endpoint("public-set-github-username", lambda: "github username set")
@json_response
def public_set_github_username():
    """
    Let the user set their github username with
    this endpoint. Some things to consider is
    making sure that the github username they
    give us has not already been taken.

    :return:
    """

    # Get the current user
    user = current_user()

    # Read the github username from the http query
    github_username = request.args.get("github_username", default=None)

    # Verify that a github username was given to us
    if github_username is None:
        return error_response("missing field")

    # Take of any whitespace that may be in the github username
    github_username = github_username.strip()

    # Check to see if there is any whitespace in the username
    if any(i in string.whitespace for i in github_username):
        return error_response("Your github username cannot have spaces")

    # Do some very basic checks on the github username they
    # gave us. We check to see that all the characters are
    # either ascii letters, digits, underscores or hyphen.
    #
    # We also check that their username did not start with
    # hyphens. This check is very simple, and may not cover
    # all the allowed rules that github puts on their
    # username.
    if not (
            all(i in (string.ascii_letters + string.digits + "-_") for i in github_username)
            and not github_username.startswith("-")
            and not github_username.endswith("-")
    ):
        # Give them back an error saying they have illegal characters
        return error_response(
            "Github usernames may only contain alphanumeric characters "
            "or single hyphens, and cannot begin or end with a hyphen."
        )

    # Check to see if the github username they gave us belongs to
    # someone else in the system.
    other = User.query.filter(
        User.id != user.id,
        User.github_username == github_username
    ).first()

    # If there is someone else in anubis that has that username,
    # then we should give back an error
    if other:
        return error_response('That github username is already taken!')

    # If all the tests and checks pass, then we can update their github username
    user.github_username = github_username

    # Then commit the change
    db.session.add(user)
    db.session.commit()

    # And give back the new github username as the response
    return success_response(github_username)
