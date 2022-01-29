import functools
from datetime import datetime, timedelta
from hashlib import sha512
from json import dumps
from os import environ, urandom
from typing import Tuple, Union

from flask import Response, has_app_context, has_request_context

from anubis.config import config
from anubis.utils.exceptions import AssertError

MYSQL_TEXT_MAX_LENGTH = 2 ** 16 - 1


def is_debug() -> bool:
    """
    Returns true if the app is running in debug mode

    :return:
    """
    return config.DEBUG


def is_job() -> bool:
    """
    Returns true if the app context is used in a job.

    :return:
    """

    return config.JOB


def jsonify(data, status_code=200):
    """
    Wrap a data response to set proper headers for json
    """
    res = Response(dumps(data))
    res.status_code = status_code
    res.headers["Content-Type"] = "application/json"
    res.headers["Access-Control-Allow-Origin"] = (
        "https://nyu.cool" if not environ.get("DEBUG", False) else "https://localhost"
    )
    return res


def verify_data_shape(data, shape, path=None) -> Tuple[bool, Union[str, None]]:
    """
    _verify_data_shape(
      {'data': []},
      {'data': list}
    ) == (True, None)

    _verify_data_shape(
      {'data': ''},
      {'data': list}
    ) == (False, '.data')

    _verify_data_shape(
      {'data': '', 'empty': 10},
      {'data': list}
    ) == (False, '.data')

    This function is what handles the data shape verification. You can use this function, or
    the decorator on uploaded data to verify its use before usage. You can basically write out
    what the shape should look like. This function supports nested dictionaries.

    Here, we will return a tuple of a boolean indicating success or failure, and a error string.
    If there was an error validating a given field, the error string will be a path to the
    unvalidated field. An example would be:

    _verify_data_shape(
      {'data': ''},
      {'data': list}
    ) -> (False, '.data')

    :return: success as bool, error path
    """

    if path is None:
        path = ""

    if shape is dict or shape is list:  # Free, just need a match
        if isinstance(data, shape):
            return True, None
        return False, path

    # Verify if data is constant
    for _t in [int, str, float]:
        if isinstance(data, _t):
            return (True, None) if shape == _t else (False, path)

    if isinstance(data, dict):  # Verify dict keys
        for s_key, s_value in shape.items():

            # Verify key is included
            if s_key not in data:
                return False, path + "." + s_key

            # Supported basic types
            for _t in [int, str, float]:

                # Check free strings are strings and lists
                if s_value is _t:
                    if not isinstance(data[s_key], s_value):
                        return False, path + "." + s_key

                # Check explicit strings and lists
                elif isinstance(s_value, _t):
                    if not isinstance(data[s_key], type(s_value)):
                        return False, path + "." + s_key

            # Recurse on other dicts
            if isinstance(s_value, dict):

                # Free dict ( no need to verify more )
                if s_value == dict:
                    return True, None

                # Explicit Dict ( need to recurse )
                elif isinstance(s_value, dict):
                    # Recurse on dict
                    r, e = verify_data_shape(data[s_key], s_value, path + "." + s_key)

                    if r is False:
                        return r, e

                # Type s_value was not dict ( type mismatch )
                else:
                    return False, path + "." + s_key

            # Recurse on lists
            if isinstance(s_value, list):
                # Free list ( no need to verify more )
                if s_value == list:
                    return True, None

                # Explicit list ( need to recurse )
                elif isinstance(s_value, list):

                    # If we have a type specified in the list,
                    # we should iterate, then recurse on the
                    # elements of the data. Otherwise there's
                    # nothing to do.
                    if len(s_value) == 1:
                        s_value = s_value[0]

                        for item in data[s_key]:
                            # Recurse on list item
                            r, e = verify_data_shape(item, s_value, path + ".[" + s_key + "]")

                            if r is False:
                                return r, e

                # Type s_value was not dict ( type mismatch )
                else:
                    return False, path + "." + s_key

            if s_value is list or s_value is dict:
                if isinstance(data[s_key], s_value):
                    return True, None
                return (
                    False,
                    path + ".[" + s_key + "]" if s_value is list else path + "." + s_key + "",
                )

    return True, None


def split_chunks(lst, n):
    """
    Split lst into list of lists size n.

    :return: list of lists
    """
    _chunks = []
    for i in range(0, len(lst), n):
        _chunks.append(lst[i: i + n])
    return _chunks


def rand(max_len: int = None):
    """
    Get a relatively random hex string of up
    to max_len.

    :param max_len:
    :return:
    """
    rand_hash = sha512(urandom(32)).hexdigest()
    if max_len is not None:
        return rand_hash[:max_len]
    return rand_hash


def human_readable_to_bytes(size: str) -> int:
    """
    Convert a string in the form of 5GB and get an integer value
    for the number of bytes in that data size.

    >>> human_readable_to_bytes('1 GiB')
    >>> 1073741824

    :param size:
    :return:
    """
    size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    size = size.split()  # divide '1 GB' into ['1', 'GB']
    num, unit = int(size[0]), size[1]
    # index in list of sizes determines power to raise it to
    idx = size_name.index(unit)
    # ** is the "exponent" operator - you can use it instead of math.pow()
    factor = 1024 ** idx
    return num * factor


def human_readable_datetime(delta: timedelta) -> str:
    """
    Take a timedelta and give a human-readable string
    version.

    >>> d = timedelta(days=2, hours=1, seconds=10)
    >>> human_readable_datetime(d)
    >>> '2d 1h 10s'

    :param delta:
    :return: string version of delta
    """
    years = delta.days // 365
    weeks = (delta.days % 365) // 7
    days = delta.days % 7
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    r = f"{seconds}s"
    if minutes > 0:
        r = f"{minutes}m " + r
    if hours > 0:
        r = f"{hours}h " + r
    if days > 0:
        r = f"{days}d " + r
    if weeks > 0:
        r = f"{weeks}w " + r
    if years > 0:
        r = f"{years}y " + r
    return r


def row2dict(row) -> dict:
    """
    Convert an sqlalchemy object to a dictionary from its column
    values. This function looks at internal sqlalchemy fields
    to create a raw dictionary from the columns in the table.

    * Something to note is that datetime object fields will be
    converted to strings in the response *

    :param row:
    :return:
    """

    raw = {}

    # Read through the sqlalchemy internal
    # column values.
    for column in row.__table__.columns:

        # Get the value corresponding to the
        # name of the column.
        value = getattr(row, column.name)

        # If the value is a datetime object, then
        # we need to convert it to a string to
        # maintain that the response is a simple
        # dictionary.
        if isinstance(value, datetime):
            value = str(value)

        # Write the column value into the response
        # dictionary.
        raw[column.name] = value

    return raw


def with_context(function):
    """
    This decorator is meant to save time and repetitive initialization
    when using flask-sqlalchemy outside of an app_context.

    :param function:
    :return:
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        # Do the import here to avoid circular
        # import issues.
        from anubis.app import create_app

        # Only create an app context if
        # there is not already one
        if has_app_context() or has_request_context():
            return function(*args, **kwargs)

        # Create a fresh app
        app = create_app()

        # Push an app context
        with app.app_context():
            with app.test_request_context():
                # Call the function within an app context
                return function(*args, **kwargs)

    return wrapper


def req_assert(*expressions, message: str = "invalid", status_code: int = 200):
    """
    Call this at any point to check if an expression is True. If any
    of the expressions provided are False, then an anubis.utils.exceptions.AssertError
    will be raised. The global handler will then use the message and status
    code in a error_response.

    >>> thing = None
    >>> req_assert(thing is not None, message='thing was None')
    >>> # raise AssertError('thing was None', 200)

    :param expressions:
    :param message:
    :param status_code:
    :return:
    """
    if not all(expressions):
        raise AssertError(message, status_code)


