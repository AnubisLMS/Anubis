import logging
from functools import wraps

from flask import request

from anubis.models import User
from anubis.utils.data import error_response


def load_from_id(model, verify_owner=True):
    def wrapper(func):
        @wraps(func)
        def decorator(id, *args, **kwargs):
            r = model.query.filter_by(id=id).first()
            if r is None or (verify_owner and User.current_user().id != r.owner.id):
                logging.info("Unauthenticated GET {}".format(request.path))
                return error_response("Unable to find"), 400
            return func(r, *args, **kwargs)

        return decorator

    return wrapper


def require_user(func):
    """
    Wrap a function to require a user to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        u = User.current_user()
        if u is None:
            return error_response('Unauthenticated'), 401
        return func(*args, **kwargs)

    return wrapper


def require_admin(func):
    """
    Wrap a function to require an admin to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        u = User.current_user()
        if u is None or u.is_admin is False:
            return error_response('Unauthenticated'), 401
        return func(*args, **kwargs)

    return wrapper
