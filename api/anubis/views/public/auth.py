from flask import Blueprint, make_response, redirect, request

from anubis.models import User, db
from anubis.utils.assignment.assignments import get_courses, get_assignments
from anubis.utils.users.auth import create_token, current_user, require_user
from anubis.utils.http.data import is_debug
from anubis.utils.http.decorators import json_endpoint
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.http.https import success_response, error_response
from anubis.utils.services.oauth import OAUTH_REMOTE_APP as provider
from anubis.utils.assignment.submissions import fix_dangling

auth = Blueprint("public-auth", __name__, url_prefix="/public/auth")
oauth = Blueprint("public-oauth", __name__, url_prefix="/public")


@auth.route("/login")
@log_endpoint("public-login", lambda: "login")
def public_login():
    if is_debug():
        return "AUTH"
    return provider.authorize(
        callback="https://anubis.osiris.services/api/public/oauth"
    )


@auth.route("/logout")
@log_endpoint("public-logout", lambda: "logout")
def public_logout():
    r = make_response(redirect("/"))
    r.set_cookie("token", "")
    return r


@oauth.route("/oauth")
@log_endpoint("public-oauth", lambda: "oauth")
def public_oauth():
    """
    This is the endpoint NYU oauth sends the user to after
    authentication. Here we need to verify the oauth response,
    and log them in on our side.

    There is a bit of extra work if they are a new user. When a new
    user signs in, we create their user object in the database.

    :return:
    """

    # Get the next url if it was specified.
    next_url = request.args.get("next") or "/courses"

    # Get the authorized response from NYU oauth
    resp = provider.authorized_response()
    if resp is None or "access_token" not in resp:
        return "Access Denied"

    # This is the data we get from NYU's oauth. It has basic information
    # on who is logging in
    user_data = provider.get("userinfo?schema=openid", token=(resp["access_token"],))

    # Load the netid name from the response
    netid = user_data.data["netid"]
    firstname = user_data.data["firstname"]
    lastname = user_data.data["lastname"]
    name = f'{firstname} {lastname}'.strip()

    # Check to see if user already exists
    u = User.query.filter(User.netid == netid).first()

    # Create the user if they do not already exist
    if u is None:
        u = User(netid=netid, name=name, is_admin=False)
        db.session.add(u)
        db.session.commit()

    # If their github username is not set, send them to
    # the profile page
    if u.github_username is None:
        next_url = "/profile"

    # Make the response depending on if a next_url was specified
    r = make_response(redirect(next_url))

    # Set the token cookie
    r.set_cookie("token", create_token(u.netid))

    return r


@auth.route("/whoami")
def public_whoami():
    """
    Figure out who you are

    :return:
    """
    u: User = current_user()
    if u is None:
        return success_response({})

    # If their github username is not set, then we want to send
    # a warning telling the user they need to set it in their
    # profile panel.
    status = None
    if u.github_username is None:
        status = "Please set your github username in your profile so we can identify your repos!"

    return success_response(
        {
            "user": u.data,
            "classes": get_courses(u.netid),
            "assignments": get_assignments(u.netid),
            "status": status,
            "variant": "warning",
        }
    )


@auth.route("/set-github-username", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("github_username", str)])
def public_auth_set_github_username(github_username):
    """
    Sets a github username for the current user.

    :return:
    """

    user: User = current_user()

    # Make sure github username was specified
    if github_username is None:
        return error_response("github username not specified")

    # Make sure the github username is not already being used
    other: User = User.query.filter(
        User.github_username == github_username, User.id != user.id
    ).first()
    if other is not None:
        return error_response("github username is already taken")

    # Set github username and commit
    user.github_username = github_username
    db.session.add(user)
    db.session.commit()

    # Run the fix dangling in case there are some
    # dangling submissions they have created.
    fix_dangling()

    # Notify them with status
    return success_response({"status": "github username updated"})
