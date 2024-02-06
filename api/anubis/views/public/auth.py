import traceback
from urllib.parse import urlunparse
from urllib.parse import quote

import json
import requests
from flask import Blueprint, make_response, redirect, request

from anubis.constants import NYU_DOMAIN
from anubis.env import env
from anubis.lms.courses import get_course_context
from anubis.models import User, db, UserSource
from anubis.utils.auth.oauth import OAUTH_REMOTE_APP_GITHUB as github_provider
from anubis.utils.auth.oauth import OAUTH_REMOTE_APP_NYU as nyu_provider
from anubis.utils.auth.token import create_token
from anubis.utils.auth.user import current_user, get_current_user
from anubis.utils.data import is_debug
from anubis.utils.http import success_response, get_string_arg
from anubis.utils.exceptions import AuthenticationError
from anubis.utils.config import get_config_str
from anubis.utils.logging import logger


auth_ = Blueprint("public-auth", __name__, url_prefix="/public/auth")
nyu_oauth_ = Blueprint("public-oauth", __name__, url_prefix="/public")
github_oauth_ = Blueprint("public-github-oauth", __name__, url_prefix="/public/github")


@auth_.route("/login")
def public_login():
    if is_debug():
        return "AUTH"
    return nyu_provider.authorize(callback="https://{}/api/public/oauth".format(NYU_DOMAIN))


@auth_.route("/logout")
def public_logout():
    r = make_response(redirect("/"))
    r.set_cookie("token", "")
    return r


@auth_.route("/oauth-workaround")
def public_nyu_oauth_workaround():
    token = request.args.get('token', None)
    next_url = request.args.get('next') or None

    if token is None:
        return 'Error', 400

    # Make the response depending on if a next_url was specified
    r = make_response(redirect(next_url))

    # set the token cookie
    r.set_cookie("token", token, httponly=True)

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
    next_url = "/playgrounds"

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
        user = User(netid=netid, name=name, source=UserSource.NYU)
        db.session.add(user)
        db.session.commit()

    # If their github username is not set, send them to
    # the profile page
    if user.github_username is None:
        next_url = "/profile"

    # Make the response depending on if a next_url was specified
    token = create_token(user.netid)
    r = make_response(redirect(urlunparse((
        'https', env.DOMAIN, '/api/public/auth/oauth-workaround', '', f'next={quote(next_url)}&token={quote(token)}', ''
    ))))

    return r


@github_oauth_.route("/login")
def public_github_link():
    if current_user is None:
        user_access_code: str | None = get_string_arg('access_code', default_value=None)
        real_access_code: str = get_config_str('GITHUB_STUDY_ACCESS_CODE', None)

        # If either are not set, raise
        if user_access_code is None or real_access_code is None:
            raise AuthenticationError()

        # If either are not strings
        if not isinstance(user_access_code, str) or not isinstance(real_access_code, str):
            raise AuthenticationError()

        # If they don't match
        if user_access_code != real_access_code:
            raise AuthenticationError()

    return github_provider.authorize(callback="https://{}/api/public/github/oauth".format(env.DOMAIN))


@github_oauth_.route("/oauth")
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

    # setup headers and url
    github_api_headers = {
        "authorization": "bearer " + resp["access_token"],
        "accept":        "application/vnd.github.v3+json",
    }
    github_api_url = "https://api.github.com/user"

    try:
        # Request Github User API
        github_user_info = requests.get(
            github_api_url,
            headers=github_api_headers,
        ).json()

        # Display user info
        logger.info(f'github_user_info = {json.dumps(github_user_info, indent=2)}')

        # Get minimal information for setting username
        github_username = github_user_info["login"].strip()

        # If user exists
        if current_user is not None:
            # set github username and commit
            current_user.github_username = github_username
            db.session.add(current_user)
            db.session.commit()

        # Create new user for study
        else:
            # Check to see if user already exists in system. This sound fix anyone that already has an anubis NYU account
            user = User.query.filter(User.github_username == github_username).first()

            # If user didn't already exist, we need to create one
            if user is None:

                # Grab email to use as netid
                github_netid = f"github{github_user_info['id']}"
                name = github_user_info['name'].strip() if 'name' in github_user_info else github_netid

                # Create user
                user = User(
                    netid=github_netid,
                    name=name,
                    github_username=github_username,

                    # Be sure to mark GITHUB source
                    source=UserSource.GITHUB,
                )

                # Commit change
                db.session.add(user)
                db.session.commit()

            # Make the response depending on if a next_url was specified
            r = make_response(redirect(next_url))

            # set the token cookie
            token = create_token(user.netid)
            r.set_cookie("token", token, httponly=True)

            # Return response
            return r

        # Notify them with status
        return redirect(next_url)
    except Exception as e:
        logger.error(traceback.format_exc())
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
            "user":    None,
            "context": None,
        })

    course_context = None
    context = get_course_context(False)
    if context is not None:
        course_context = {
            "id":   context.id,
            "name": context.name,
        }

    return success_response(
        {
            "user":    current_user.data,
            "context": course_context,
            "variant": "warning",
        }
    )
