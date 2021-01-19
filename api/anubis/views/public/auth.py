from flask import Blueprint, make_response, redirect, request

from anubis.models import User, db
from anubis.utils.assignments import get_courses, get_assignments
from anubis.utils.auth import create_token, current_user
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response, error_response
from anubis.utils.oauth import OAUTH_REMOTE_APP as provider
from anubis.utils.submissions import fix_dangling
from anubis.utils.auth import require_user
from anubis.utils.decorators import json_endpoint
from anubis.utils.data import is_debug

auth = Blueprint("public-auth", __name__, url_prefix="/public/auth")


@auth.route("/login")
@log_endpoint("public-login", lambda: "login")
def public_login():
    if is_debug():
        return "AUTH"
    return provider.authorize(
        callback="https://anubis.osiris.services/api/public/auth/oauth"
    )


@auth.route("/logout")
@log_endpoint("public-logout", lambda: "logout")
def public_logout():
    r = make_response(redirect("/"))
    r.set_cookie("token", "")
    return r


@auth.route("/oauth")
@log_endpoint("public-oauth", lambda: "oauth")
def public_oauth():
    next_url = request.args.get("next") or "/courses"
    resp = provider.authorized_response()
    if resp is None or "access_token" not in resp:
        return "Access Denied"

    user_data = provider.get("userinfo?schema=openid", token=(resp["access_token"],))

    netid = user_data.data["netid"]
    name = user_data.data["firstname"] + " " + user_data.data["lastname"]

    u = User.query.filter(User.netid == netid).first()
    if u is None:
        u = User(netid=netid, name=name, is_admin=False)
        db.session.add(u)
        db.session.commit()

    if u.github_username is None:
        next_url = "/set-github-username"

    fix_dangling()

    r = make_response(redirect(next_url))
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

    fix_dangling()

    return success_response({"status": "github username updated"})
