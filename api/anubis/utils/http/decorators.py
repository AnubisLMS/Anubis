import logging
from functools import wraps
from typing import Union, List, Tuple

from flask import request

from anubis.models import Submission
from anubis.utils.users.auth import current_user
from anubis.utils.http.data import jsonify, _verify_data_shape
from anubis.utils.http.https import error_response


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


def json_endpoint(
        required_fields: Union[List[str], List[Tuple], None] = None,
        only_required: bool = False,
):
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
            if not request.headers.get("Content-Type", default=None).startswith(
                    "application/json"
            ):
                return {
                           "success": False,
                           "error": "Content-Type header is not application/json",
                           "data": None,
                       }, 406  # Not Acceptable
            json_data: dict = request.json

            if required_fields is not None:
                # Check required fields
                for index, field in enumerate(required_fields):
                    # If field was a tuple, extract field name and required
                    # type
                    required_type = None
                    if isinstance(field, tuple):
                        field, required_type = field
                        required_fields[index] = field

                    # Make sure
                    if field not in json_data:
                        # field missing, return error
                        return (
                            error_response(
                                "Malformed requests. Missing field {}.".format(field)
                            ),
                            406,
                        )  # Not Acceptable

                    # If a type was specified, verify it
                    if required_type is not None:
                        if not isinstance(json_data[field], required_type):
                            return (
                                error_response(
                                    "Malformed requests. Invalid field type."
                                ),
                                406,
                            )  # Not Acceptable

            # Give the positional args first,
            # then the json data (in the order of
            # the required fields), and lastly
            # the kwargs that were passed in.
            if required_fields is not None:

                # We can optionally specify only_required to
                # skip this step. Here we are adding the key
                # values from the posted json to the kwargs
                # of the function. This is potentially destructive
                # as it will overwrite any keys already in the
                # kwargs with the values in the json.
                if not only_required:
                    for key, value in json_data.items():
                        if key not in required_fields:
                            kwargs[key] = value

                # Call the function while trying to maintain a
                # logical order to the arguments
                return func(
                    *args,
                    **{field: json_data[field] for field in required_fields},
                    **kwargs,
                )
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
    def wrapper(submission_id: str):
        submission = Submission.query.filter(Submission.id == submission_id).first()
        token = request.args.get("token", default=None)

        # Verify submission exists
        if submission is None:
            logging.error(
                "Invalid submission from submission pipeline",
                extra={
                    "submission_id": submission_id,
                    "path": request.path,
                    "headers": request.headers,
                    "ip": request.remote_addr,
                },
            )
            return error_response("Invalid"), 406

        # Verify we got a token
        if token is None:
            logging.error(
                "Attempted report post with no token",
                extra={
                    "submission_id": submission_id,
                    "path": request.path,
                    "headers": request.headers,
                    "ip": request.remote_addr,
                },
            )
            return error_response("Invalid"), 406

        # Verify token matches
        if token != submission.token:
            logging.error(
                "Invalid token reported from pipeline",
                extra={
                    "submission_id": submission_id,
                    "path": request.path,
                    "headers": request.headers,
                    "ip": request.remote_addr,
                },
            )
            return error_response("Invalid"), 406

        logging.info("Pipeline request validated {}".format(request.path))
        return func(submission)

    return wrapper


def verify_shape(*shapes):
    """
    This is the decorator form of the data shape verification function. It will validate the
    arguments of a function before calling it. You can just sequentially provide the expected shapes
    of the arguments. It will return error_response's if there was a problem validating something.

    :param shapes: sequence of argument shapes
    :return: error_response on error
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # We should reject if we're not able to use all our shapes
            if len(args) < len(shapes):
                return error_response("Missing fields"), 406

            # Verify our argument shapes
            for data, shape in zip(args, shapes):
                r, e = _verify_data_shape(data, shape)
                if not r:
                    return error_response("Shape invalid {}".format(e)), 406

            # Shapes pass, run function
            return func(*args, **kwargs)

        return wrapper

    return decorator
