import traceback
from typing import Union, Callable, Optional, Any

import jwt
from flask import g
from werkzeug.local import LocalProxy

from anubis.config import config
from anubis.models import User
from anubis.utils.auth.token import get_token
from anubis.utils.logging import logger


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
        logger.error("AUTH decode error\n" + traceback.format_exc())
        return None

    # Make sure there is a netid in the jwt
    if "netid" not in decoded:
        return None

    # Get the user from the decoded jwt
    netid = decoded["netid"]
    user = User.query.filter_by(netid=netid).first()

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


current_user: User = LocalProxy(get_current_user)
