import string

from flask import Blueprint, request

from anubis.models import User, db
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response

profile = Blueprint("public-profile", __name__, url_prefix="/public/profile")


@profile.route("/toggle-email-notifications/<string:key>")
@require_user()
@json_response
def public_profile_toggle_email_notifications(key: str):
    status: str | None = None

    match key:
        case "deadline_email_enabled":
            current_user.deadline_email_enabled = not current_user.deadline_email_enabled
            status = "Deadline Notification " + ("Enabled" if current_user.deadline_email_enabled else "Disabled")
        case "release_email_enabled":
            current_user.release_email_enabled = not current_user.release_email_enabled
            status = "Release Notification " + ("Enabled" if current_user.release_email_enabled else "Disabled")

    db.session.add(current_user)
    db.session.commit()

    return success_response({
        "user": current_user.data,
        "status": status,
        "variant": "success",
    })


@profile.route("/set-github-username")
@require_user()
@json_response
def public_set_github_username():
    """
    Let the user set their github username with
    this endpoint. Some things to consider is
    making sure that the github username they
    give us has not already been taken.

    :return:
    """

    # Read the github username from the http query
    github_username = request.args.get("github_username", default=None)

    # Verify that a github username was given to us
    req_assert(github_username is not None, message="missing github_username")

    # Take of any whitespace that may be in the github username
    github_username = github_username.strip()

    # Make sure it is not an empty string
    req_assert(len(github_username) > 0, message="Please provide at least one character")

    # Make sure it is not too long
    req_assert(len(github_username) < 512, message="Please provide less than 512 characters")

    # Check to see if there is any whitespace in the username
    req_assert(
        all(i not in string.whitespace for i in github_username),
        message="github username cannot have whitespace",
    )

    # Do some very basic checks on the github username they
    # gave us. We check to see that all the characters are
    # either ascii letters, digits, underscores or hyphen.
    #
    # We also check that their username did not start with
    # hyphens. This check is very simple, and may not cover
    # all the allowed rules that github puts on their
    # username.
    req_assert(
        all(i in (string.ascii_letters + string.digits + "-_") for i in github_username),
        not github_username.startswith("-"),
        not github_username.endswith("-"),
        message="Github usernames may only contain alphanumeric characters "
                "or single hyphens, and cannot begin or end with a hyphen.",
    )

    # Check to see if the github username they gave us belongs to
    # someone else in the system.
    other = User.query.filter(User.id != current_user.id, User.github_username == github_username).first()

    # If there is someone else in anubis that has that username,
    # then we should give back an error
    req_assert(other is None, message="That github username is already taken!")

    # If all the tests and checks pass, then we can update their github username
    current_user.github_username = github_username

    # Then commit the change
    db.session.add(current_user)
    db.session.commit()

    # And give back the new github username as the response
    return success_response(github_username)
