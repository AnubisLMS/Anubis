import functools
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Union

import jwt
from flask import g
from flask import request

from anubis.config import config
from anubis.models import User, TAForCourse, ProfessorForCourse
from anubis.utils.data import is_debug
from anubis.utils.http.https import error_response, get_request_ip
from anubis.utils.services.logger import logger


class AuthenticationError(Exception):
    """
    This exception should be raised if a request
    lacks the proper authentication fow whatever
    action they are requesting.

    If the view function is wrapped in any of the
    require auth decorators, then this exception
    will be caught and return a 401.
    """


class LackCourseContext(Exception):
    """
    Most of the admin actions require there to
    be a course context to be set. This exception
    should be raised if there is not a course
    context set.

    If there is some other permission issue involving
    the course context, then a AuthenticationError
    may be more appropriate.
    """


def get_user(netid: Union[str, None]) -> Union[User, None]:
    """
    Load a user by username

    :param netid: netid of wanted user
    :return: User object or None
    """
    if netid is None:
        return None

    # Get the user from the database
    user = User.query.filter_by(netid=netid).first()

    return user


def current_user() -> Union[User, None]:
    """
    Load current user based on the token

    :return: User or None
    """
    if g.get("user", default=None) is not None:
        return g.user

    # Attempt to get the token from the request
    token = get_token()
    if token is None:
        return None

    # Try to decode the jwt
    try:
        decoded = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        logger.error('AUTH decode error\n' + traceback.format_exc())
        return None

    # Make sure there is a netid in the jwt
    if "netid" not in decoded:
        return None

    # Get the user from the decoded jwt
    user = get_user(decoded["netid"])

    # Cache the user in the request context
    g.user = user

    return user


def get_token() -> Union[str, None]:
    """
    Attempt to get the token from the request. Both the cookie, and the
    headers will be checked.

    :return:
    """

    return request.headers.get("token", default=None) or request.cookies.get(
        "token", default=None
    ) or request.args.get('token', default=None)


def create_token(netid: str, **extras) -> Union[str, None]:
    """
    Get token for user by netid

    :param netid:
    :return: token string or None (if user not found)
    """

    # Get user
    user: User = get_user(netid)

    # Verify user exists
    if user is None:
        return None

    # Create new token
    return jwt.encode({
        "netid": user.netid,
        "exp": datetime.utcnow() + timedelta(hours=6),
        **extras,
    }, config.SECRET_KEY)


def _course_context_wrapper(function):
    """
    Wrap a view function or view decorator with a
    LackCourseContext handler. This should be applied
    to the admin require decorators.

    :param function:
    :return:
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except LackCourseContext as e:
            logger.error(traceback.format_exc())
            return error_response(str(e) or 'Please set your course context')

    return wrapper


def _auth_context_wrapper(function):
    """
    Wrap a view function or decorator with an
    AuthenticationError handler. It will handle
    the exception with a 401. This should be
    applied to all the require decorators.

    :param function:
    :return:
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except AuthenticationError as e:
            logger.error(traceback.format_exc())
            return error_response(str(e) or 'Unauthenticated'), 401

    return wrapper


def require_user(unless_debug=False):
    """
    Wrap a function to require a user to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :return:
    """

    def decorator(func):
        @wraps(func)
        @_auth_context_wrapper
        @_course_context_wrapper
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = current_user()

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is an admin.
            if user is None:
                return error_response("Unauthenticated"), 401

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_admin(unless_debug=False, unless_vpn=False):
    """
    Wrap a function to require an admin to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :param unless_vpn:
    :return:
    """

    def decorator(func):
        @wraps(func)
        @_auth_context_wrapper
        @_course_context_wrapper
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = current_user()

            # Bypass auth if vpn
            if unless_vpn and get_request_ip() == '128.238.66.211':
                return func(*args, **kwargs)

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is an admin.
            if user is None:
                raise AuthenticationError('Request is anonymous')

            if user.is_superuser:
                return func(*args, **kwargs)

            ta = TAForCourse.query.filter(
                TAForCourse.owner_id == user.id).first()
            prof = ProfessorForCourse.query.filter(
                ProfessorForCourse.owner_id == user.id).first()

            if ta is None and prof is None:
                raise AuthenticationError('User is not ta or professor')

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_superuser(unless_debug=False, unless_vpn=False):
    """
    Wrap a function to require an superuser to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :param unless_vpn:
    :return:
    """

    def decorator(func):
        @wraps(func)
        @_auth_context_wrapper
        @_course_context_wrapper
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = current_user()

            # Bypass auth if vpn
            if unless_vpn and get_request_ip() == '128.238.66.211':
                return func(*args, **kwargs)

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is a superuser.
            if user is None:
                return error_response("Unauthenticated"), 401

            # If the user is not a superuser, then return a 400 error
            # so it will be displayed in a snackbar.
            if user.is_superuser is False:
                return error_response("Requires superuser")

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator
