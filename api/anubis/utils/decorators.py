import logging
from functools import wraps
from typing import Union, List

from flask import request

from anubis.models import User
from anubis.utils.auth import current_user
from anubis.utils.data import error_response, jsonify


def load_from_id(model, verify_owner=True):
    def wrapper(func):
        @wraps(func)
        def decorator(id, *args, **kwargs):
            r = model.query.filter_by(id=id).first()
            if r is None or (verify_owner and current_user().id != r.owner.id):
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
        u = current_user()
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


def json_response(func):
    """
    Wrap a route so that it always converts data
    response to proper json.

    @app.route('/')
    @json
    def test():
        return {
            'success': True
        }
    """

    @wraps(func)
    def json_wrap(*args, **kwargs):
        data = func(*args, **kwargs)
        status_code = 200
        if isinstance(data, tuple):
            data, status_code = data
        return jsonify(data, status_code)

    return json_wrap


def json_endpoint(required_fields: Union[List[str], None] = None):
    """
    Wrap a route so that it always converts data
    response to proper json.

    @app.route('/')
    @json
    def test():
        return {
            'success': True
        }
    """

    def wrapper(func):
        @wraps(func)
        def json_wrap(*args, **kwargs):
            if not request.headers.get('Content-Type', default=None).startswith('application/json'):
                return {
                           'success': False,
                           'error': 'Content-Type header is not application/json',
                           'data': None,
                       }, 406  # Not Acceptable
            json_data: dict = request.json

            if required_fields is not None:
                # Check required fields
                for field in required_fields:
                    if field not in json_data:
                        # field missing, return error
                        return {
                                   'success': False,
                                   'error': 'Malformed requests. Missing fields.',
                                   'data': None
                               }, 406  # Not Acceptable

            if required_fields is not None:
                return func(
                    *args,
                    *(json_data[field] for field in required_fields),
                    **{key: value for key, value in json_data.items() if key not in required_fields},
                    **kwargs)
            return func(json_data, *args, **kwargs)

        return json_wrap

    return wrapper