from email.mime.text import MIMEText
from hashlib import sha256
from json import dumps
from os import environ, urandom
from smtplib import SMTP
from typing import Union, Tuple
from datetime import datetime

from flask import Response

from anubis.config import config


def is_debug() -> bool:
    """
    Returns true if the app is running in debug mode

    :return:
    """
    return config.DEBUG


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


def send_noreply_email(message: str, subject: str, recipient: str):
    """
    Use this function to send a noreply email to a user (ie student).

    * This will only work on the computer that has the dns pointed to it (ie the server)

    If you set up the dns with namecheap, you can really easily just set
    the email dns setting to private email. Once that is set, it configures
    all the spf stuff for you. Doing to MX and spf records by hand are super
    annoying.

    eg:
    send_noreply_email('this is the message', 'this is the subject', 'netid@nyu.edu')

    :msg str: email body or message to send
    :subject str: subject for email
    :to str: recipient of email (should be their nyu email)
    """

    if environ.get("DEBUG", False):
        return print(message, subject, recipient, flush=True)

    message = MIMEText(message, "plain")
    message["Subject"] = subject

    message["From"] = "noreply@anubis.osiris.services"
    message["To"] = recipient

    s = SMTP("smtp")
    s.send_message(message)
    s.quit()


def notify(user, message: str, subject: str):
    """
    Send a noreply email to a user.

    :param user:
    :param message:
    :param subject:
    :return:
    """
    recipient = "{netid}@nyu.edu".format(netid=user.netid)
    send_noreply_email(message, subject, recipient)


def _verify_data_shape(data, shape, path=None) -> Tuple[bool, Union[str, None]]:
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
                    r, e = _verify_data_shape(data[s_key], s_value, path + "." + s_key)

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
                            r, e = _verify_data_shape(
                                item, s_value, path + ".[" + s_key + "]"
                            )

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
                    path + ".[" + s_key + "]"
                    if s_value is list
                    else path + "." + s_key + "",
                )

    return True, None


def split_chunks(lst, n):
    """
    Split lst into list of lists size n.

    :return: list of lists
    """
    _chunks = []
    for i in range(0, len(lst), n):
        _chunks.append(lst[i : i + n])
    return _chunks


def rand(max_len=None):
    rand_hash = sha256(urandom(32)).hexdigest()
    if max_len is not None:
        return rand_hash[:max_len]
    return rand_hash


def human_readable_to_bytes(size: str) -> int:
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    size = size.split()  # divide '1 GB' into ['1', 'GB']
    num, unit = int(size[0]), size[1]
    # index in list of sizes determines power to raise it to
    idx = size_name.index(unit)
    # ** is the "exponent" operator - you can use it instead of math.pow()
    factor = 1024 ** idx
    return num * factor


def row2dict(row):
    d = {}

    for column in row.__table__.columns:
        value = getattr(row, column.name)

        if isinstance(value, datetime):
            d[column.name] = str(value)
            continue

        d[column.name] = value

    return d
