from datetime import datetime, timedelta
from typing import Union

import jwt
from flask import has_request_context, request

from anubis.config import config
from anubis.models import User


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
    user: User = User.query.filter_by(netid=netid).first()

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
