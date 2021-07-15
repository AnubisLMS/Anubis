import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Union, Optional, Callable, Any

import jwt
from flask import g, request, has_request_context
from werkzeug.local import LocalProxy

from anubis.config import config
from anubis.models import User, TAForCourse, ProfessorForCourse
from anubis.utils.data import is_debug
from anubis.utils.exceptions import AuthenticationError
from anubis.utils.services.logger import logger


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


def get_current_user() -> Union[User, None]:
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


def _create_get_current_user_field(field: str) -> Callable:
    def _func() -> Optional[Any]:
        """
        Load current_user.id
        :return:
        """

        # Get current user
        user = get_current_user()

        # Make sure they exist
        if user is None:
            return None

        # Return the user.id
        return getattr(user, field)

    return _func


def get_token() -> Union[str, None]:
    """
    Attempt to get the token from the request. Both the cookie, and the
    headers will be checked.

    :return:
    """

    if not has_request_context():
        return None

    return request.headers.get("token", default=None) or request.cookies.get(
        "token", default=None
    ) or request.args.get('token', default=None)


def create_token(netid: str, exp_kwargs=None, **extras) -> Union[str, None]:
    """
    Get token for user by netid. You can provide a dictionary
    to the exp_kwargs to set a different expire time for this token.
    By default it is 6 hours. If you wanted to do 6 days exp_kwargs={'days': 6}

    :param exp_kwargs:
    :param netid:
    :return: token string or None (if user not found)
    """

    # Get user
    user: User = get_user(netid)

    if exp_kwargs is None:
        exp_kwargs = {'hours': 6}

    # Verify user exists
    if user is None:
        return None

    # Create new token
    return jwt.encode({
        "netid": user.netid,
        "exp": datetime.utcnow() + timedelta(**exp_kwargs),
        **extras,
    }, config.SECRET_KEY)


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
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = get_current_user()

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is an admin.
            if user is None:
                raise AuthenticationError()

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_admin(unless_debug=False):
    """
    Wrap a function to require an admin to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = get_current_user()

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


def require_superuser(unless_debug=False):
    """
    Wrap a function to require an superuser to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = get_current_user()

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is a superuser.
            if user is None:
                raise AuthenticationError()

            # If the user is not a superuser, then return a 400 error
            # so it will be displayed in a snackbar.
            if user.is_superuser is False:
                raise AuthenticationError("Requires superuser")

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator


current_user: User = LocalProxy(get_current_user)
