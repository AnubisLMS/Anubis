import logging
from functools import wraps
from typing import Union, List, Tuple

from flask import request

from anubis.models import User, Submission
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


def json_endpoint(required_fields: Union[List[str], List[Tuple], None] = None):
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
                for index, field in enumerate(required_fields):
                    # If field was a tuple, extract field name and required type
                    required_type = None
                    if isinstance(field, tuple):
                        field, required_type = field
                        required_fields[index] = field

                    # Make sure
                    if field not in json_data:
                        # field missing, return error
                        return error_response('Malformed requests. Missing field {}.'.format(field)), 406  # Not Acceptable

                    # If a type was specified, verify it
                    if required_type is not None:
                        if not isinstance(json_data[field], required_type):
                            return error_response('Malformed requests. Invalid field type.'), 406  # Not Acceptable

            # Give the positional args first,
            # then the json data (in the order of
            # the required fields), and lastly
            # the kwargs that were passed in.
            if required_fields is not None:
                return func(
                    *args,
                    *(json_data[field] for field in required_fields),
                    **{key: value for key, value in json_data.items() if key not in required_fields},
                    **kwargs)
            return func(json_data, *args, **kwargs)

        return json_wrap

    return wrapper


def check_submission_token(func):
    """
    This decorator should be exclusively used on the pipeline manager.
    For the report endpoints, it will find and verify submission data
    for endpoints that follow the shape:

    /report/.../<int:submission_id>?token=<token>

    If the submission and the token are not verified, and error response
    with status code 406 (rejected) will be returned.

    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(submission_id: int):
        submission = Submission.query.filter(Submission.id == submission_id).first()
        token = request.args.get('token', default=None)

        # Verify submission exists
        if submission is None:
            logging.error('Invalid submission from submission pipeline', extra={
                'submission_id': submission_id,
                'path': request.path,
                'headers': request.headers,
                'ip': request.remote_addr,
            })
            return error_response('Invalid'), 406

        # Verify we got a token
        if token is None:
            logging.error('Attempted report post with no token', extra={
                'submission_id': submission_id,
                'path': request.path,
                'headers': request.headers,
                'ip': request.remote_addr,
            })
            return error_response('Invalid'), 406

        # Verify token matches
        if token != submission.token:
            logging.error('Invalid token reported from pipeline', extra={
                'submission_id': submission_id,
                'path': request.path,
                'headers': request.headers,
                'ip': request.remote_addr,
            })
            return error_response('Invalid'), 406

        logging.info('Pipeline request validated {}'.format(request.path))
        return func(submission)
    return wrapper










