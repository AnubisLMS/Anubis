import logging
from typing import Union

import jwt
from flask import request

from anubis.models import User


def load_user(netid: Union[str, None]) -> Union[User, None]:
    """
    Load a user by username

    :param netid: netid of wanted user
    :return: User object or None
    """
    if netid is None:
        return None
    u1 = User.query.filter_by(netid=netid).first()

    logging.debug(f'loading user {u1.data}')

    return u1


def current_user() -> Union[User, None]:
    """
    Load current user based on the token

    :return: User or None
    """
    token = request.headers.get('token', default=None)
    if token is None:
        return None

    try:
        # TODO update secret key
        decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
    except Exception as e:
        return None

    if 'netid' not in decoded:
        return None

    return User.load_user(decoded['netid'])
