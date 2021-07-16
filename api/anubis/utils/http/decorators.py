from functools import wraps
from typing import Union, List, Tuple

from flask import request

from anubis.utils.auth import current_user
from anubis.utils.data import jsonify, _verify_data_shape
from anubis.utils.exceptions import AuthenticationError
from anubis.utils.http.https import error_response


def load_from_id(model, verify_owner=False):
    """
    This flask decorator loads the id kwarg passed in by flask
    and uses it to pull the sqlalchemy object corresponding to that id

    >>> @app.route('/assignment/<string:id>')
    >>> @require_user
    >>> @load_from_id(Assignment)
    >>> def view_function(assignment: Assignment):
    >>>     pass

    If the verify_owner is true, then the sqlachemy object's owner
    relationship (assuming it has one) will be checked against the
    current logged in user.

    :param model:
    :param verify_owner:
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def decorator(id, *args, **kwargs):
            # Use the id from the view functions params to query for
            # the object.
            r = model.query.filter_by(id=id).first()

            # If the sqlalchemy object was not found, then return a 400
            if r is None:
                return error_response("Unable to find"), 400

            # If the verify_owner option is on, then
            # check the object's owner against the currently
            # logged in user.
            if verify_owner and current_user.id != r.owner.id:
                raise AuthenticationError()

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
    Wrap a route so that it always converts data response to proper
    json. This decorator will save a whole lot of time verifying
    json body data.

    The required fields should be a list of either strings or tuples.

    If the required fields is a list of strings, then each of the
    strings will be verified in the json body, and passed to the
    view function as a kwarg.

    >>> @app.route('/')
    >>> @json_endpoint(['name')])
    >>> def test(name, **_):
    >>>    return {
    >>>        'success': True
    >>>    }

    If the required fields are a list of tuples, then the first item
    should be the string name of the field, then its type. When you
    specify the type in a tuple, then that fields type will also
    be verified in the json body.

    >>> @app.route('/')
    >>> @json_endpoint([('name', str)])
    >>> def test(name: str, **_):
    >>>    return {
    >>>        'success': True
    >>>    }
    """

    def wrapper(func):
        @wraps(func)
        def json_wrap(*args, **kwargs):

            # Get the content type header
            content_type = request.headers.get("Content-Type", default="")

            # Verify that the content type header was application json.
            # If the content type header is not application/json, then
            # flask will not parse the body of the request.
            if not content_type.startswith("application/json"):
                # If the content-type was not set properly, then we
                # should hand back a 406 not acceptable error code.
                return error_response("Content-Type header is not application/json"), 406

            # After verifying that the content type header was set,
            # then we can access the request json body
            json_body: dict = request.json

            # Build a list of the required field string values
            _required_fields: List[str] = []

            # If the required fields was set, then we
            # need to verify that they exist in the json
            # body, along with type checks if they were
            # specified.
            if required_fields is not None:
                # Check required fields
                for index, field in enumerate(required_fields):
                    # If field was a tuple, extract field name and required type.
                    required_type = None
                    if isinstance(field, tuple):

                        # If the tuple was more than two items, then
                        # we dont know how to handle.
                        if len(field) != 2:
                            pass

                        # Pull the field apart into the field and required type
                        field, required_type = field

                    # At this point, the tuple will have been parsed if it had one,
                    # so the field will always be a string. Add it to the running
                    # (fresh) list of required field string objects.
                    _required_fields.append(field)

                    # Make sure that the field is in the json body.
                    # If this condition is not met, then we will return
                    # a 406 not acceptable.
                    if field not in json_body:
                        # field missing, return error
                        # Not Acceptable
                        return error_response(f"Malformed requests. Missing field {field}."), 406

                    # If a type was specified, verify it
                    if required_type is not None:

                        # Do a type check on the json body field
                        if not isinstance(json_body[field], required_type):
                            # Not Acceptable
                            return error_response("Malformed requests. Invalid field type."), 406

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
                    for key, value in json_body.items():
                        if key not in _required_fields:
                            kwargs[key] = value

                # Call the function while trying to maintain a
                # logical order to the arguments
                return func(
                    *args,
                    **{field: json_body[field] for field in _required_fields},
                    **kwargs,
                )

            # If there was no required fields specified, then we can just call the
            # view function with the first argument being the json body.
            return func(json_body, *args, **kwargs)

        return json_wrap

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
