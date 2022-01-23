import requests
from flask import Blueprint, make_response, redirect, request

from anubis.config import config
from anubis.lms.courses import get_course_context
from anubis.models import User, db
from anubis.utils.auth.http import require_user
from anubis.utils.auth.oauth import OAUTH_REMOTE_APP_GITHUB as github_provider
from anubis.utils.auth.oauth import OAUTH_REMOTE_APP_NYU as nyu_provider
from anubis.utils.auth.token import create_token
from anubis.utils.auth.user import current_user, get_current_user
from anubis.utils.data import is_debug
from anubis.utils.http import success_response

auth_ = Blueprint("public-auth", __name__, url_prefix="/public/auth")
nyu_oauth_ = Blueprint("public-oauth", __name__, url_prefix="/public")
github_oauth_ = Blueprint("public-github-oauth", __name__, url_prefix="/public/github")


@auth_.route("/login")
def public_login():
    if is_debug():
        return "AUTH"
    return nyu_provider.authorize(callback="https://{}/api/public/oauth".format(config.DOMAIN))


@auth_.route("/logout")
def public_logout():
    r = make_response(redirect("/"))
    r.set_cookie("token", "")
    return r


@nyu_oauth_.route("/oauth")
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
    resp = nyu_provider.authorized_response()
    if resp is None or "access_token" not in resp:
        return "Access Denied"

    # This is the data we get from NYU's oauth. It has basic information
    # on who is logging in
    user_data = nyu_provider.get("userinfo?schema=openid", token=(resp["access_token"],))

    # Load the netid name from the response
    netid = user_data.data["netid"]
    firstname = user_data.data["firstname"]
    lastname = user_data.data["lastname"]
    name = f"{firstname} {lastname}".strip()

    # Check to see if user already exists
    user = User.query.filter(User.netid == netid).first()

    # Create the user if they do not already exist
    if user is None:
        user = User(netid=netid, name=name)
        db.session.add(user)
        db.session.commit()

    # If their github username is not set, send them to
    # the profile page
    if user.github_username is None:
        next_url = "/profile"

    # Make the response depending on if a next_url was specified
    r = make_response(redirect(next_url))

    # Set the token cookie
    r.set_cookie("token", create_token(user.netid), httponly=True)

    return r


@github_oauth_.route("/login")
@require_user()
def public_github_link():
    return github_provider.authorize(callback="https://{}/api/public/github/oauth".format(config.DOMAIN))


@github_oauth_.route("/oauth")
@require_user()
def public_github_oauth():
    """
    This is the endpoint Github OAuth sends the user to after
    authentication. Here we need to verify the oauth response,
    and update user's Github username to the database.

    :return:
    """

    # Get the next url if it was specified.
    next_url = "/profile"

    # Get the authorized response from Github OAuth
    resp = github_provider.authorized_response()
    if resp is None or "access_token" not in resp:
        return "Access Denied"

    # Setup headers and url
    github_api_headers = {
        "authorization": "bearer " + resp["access_token"],
        "accept": "application/vnd.github.v3+json",
    }
    github_api_url = "https://api.github.com/user"

    try:
        # Request Github User API
        github_user_info = requests.get(
            github_api_url,
            headers=github_api_headers,
        ).json()

        # Set github username and commit
        current_user.github_username = github_user_info["login"].strip()
        db.session.add(current_user)
        db.session.commit()

        # Notify them with status
        return redirect(next_url)
    except:
        return redirect(next_url + '?error=Unable to set username')


@auth_.route("/whoami")
def public_whoami():
    """
    Figure out who you are

    :return:
    """

    # When the current_user is None (ie no one is logged in)
    # just pass back Nones.
    if get_current_user() is None:
        return success_response({
            "user": None,
            "context": None,
        })

    course_context = None
    context = get_course_context(False)
    if context is not None:
        course_context = {
            "id": context.id,
            "name": context.name,
        }

    return success_response(
        {
            "user": current_user.data,
            "context": course_context,
            "variant": "warning",
        }
    )
