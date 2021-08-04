import base64
import json
import os

from flask import Blueprint, make_response, redirect, request

from anubis.models import User, db
from anubis.utils.auth import create_token, current_user, require_user, require_admin
from anubis.utils.data import is_debug, req_assert
from anubis.utils.http.decorators import json_endpoint
from anubis.utils.http.https import success_response, error_response
from anubis.utils.lms.courses import get_course_context
from anubis.utils.lms.submissions import fix_dangling
from anubis.utils.services.oauth import OAUTH_REMOTE_APP as provider

auth_ = Blueprint("public-auth", __name__, url_prefix="/public/auth")
oauth_ = Blueprint("public-oauth", __name__, url_prefix="/public")


@auth_.route("/login")
def public_login():
    if is_debug():
        return "AUTH"
    return provider.authorize(
        callback="https://anubis.osiris.services/api/public/oauth"
    )


@auth_.route("/logout")
def public_logout():
    r = make_response(redirect("/"))
    r.set_cookie("token", "")
    return r


@oauth_.route("/oauth")
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


@auth_.route("/whoami")
def public_whoami():
    """
    Figure out who you are

    :return:
    """

    # If their github username is not set, then we want to send
    # a warning telling the user they need to set it in their
    # profile panel.
    status = None
    if current_user.github_username is None:
        status = "Please set your github username in your profile so we can identify your repos!"

    course_context = None
    context = get_course_context(False)
    if context is not None:
        course_context = {
            "id": context.id,
            "name": context.name,
        }

    return success_response({
        "user": current_user.data,
        "context": course_context,
        "status": status,
        "variant": "warning",
    })


@auth_.route("/set-github-username", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("github_username", str)])
def public_auth_set_github_username(github_username):
    """
    Sets a github username for the current user.

    :return:
    """

    # Make sure github username was specified
    if github_username is None:
        return error_response("github username not specified")

    # Make sure the github username is not already being used
    other: User = User.query.filter(
        User.github_username == github_username, User.id != current_user.id
    ).first()

    # Assert that there is not a duplicate github username
    req_assert(other is None, message='github username is already taken')

    # Set github username and commit
    current_user.github_username = github_username
    db.session.add(current_user)
    db.session.commit()

    # Run the fix dangling in case there are some
    # dangling submissions they have created.
    fix_dangling()

    # Notify them with status
    return success_response({"status": "github username updated"})


@auth_.route('/cli')
@require_admin()
def public_cli_auth():
    """
    When the cli authenticates it will open a browser window that will authenticate then
    ?next them to here. This should redirect the user back to the local server that
    is running with whatever authentication token it needs.

    :return:
    """

    # Create a token with 30 days to expire
    token = create_token(current_user.netid, exp_kwargs={'days': 30})

    # Grab the docker config out of the environ if it is there
    docker_token = os.environ.get('DOCKER_TOKEN', None)
    docker_registry = os.environ.get('DOCKER_REGISTRY', None)
    docker_config = {
        'registry': docker_registry,
        'token': docker_token,
    }
    if docker_token is None or docker_registry is None:
        docker_config = None

    # Construct the data response
    data = json.dumps({
        'token': token,
        'docker_config': docker_config,
    })

    # Base64 encode the response
    b64_encoded_data = base64.b64encode(data.encode()).decode()

    # Construct message to be splayed on the browser
    message = f'Please copy this into the cli console:\n{b64_encoded_data}'

    # Create the response
    response = make_response(message)

    # Set the content type to text/plain so that there is no additional
    # formatting added to the browser display
    response.headers['Content-Type'] = 'text/plain'

    return response
