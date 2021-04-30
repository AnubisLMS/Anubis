from datetime import datetime, timedelta
from typing import Union, Tuple

from flask import request


def get_request_ip():
    """
    Since we are using a request forwarder,
    the real client IP will be added as a header.
    This function will search the expected headers
    to find that ip.
    """

    def check(header):
        """get header from request else empty string"""
        return request.headers[header] if header in request.headers else ""

    def check_(headers, n=0):
        """check headers based on ordered piority"""
        if n == len(headers):
            return ""
        return check(headers[n]) or check_(headers, n + 1)

    return str(
        check_(
            [
                "x-forwarded-for",  # highest priority
                "X-Forwarded-For",
                "x-real-ip",
                "X-Real-Ip",  # lowest priority
            ]
        )
        or request.remote_addr
        or "N/A"
    )


def error_response(error_message: str) -> dict:
    """
    Form an error REST api response dict.

    :param error_message: string error message
    :return:
    """
    return {
        "success": False,
        "error": error_message,
        "data": None,
    }


def success_response(data: Union[dict, str, None]) -> dict:
    """
    Form a success REST api response dict.

    :param data:
    :return:
    """
    return {
        "success": True,
        "error": None,
        "data": data,
    }


def get_number_arg(arg_name: str = "number", default_value: int = 10, reject_negative: bool = True) -> int:
    """
    Quick function for getting a number http query argument. If the
    argument is not found, or cannot be converted to an int
    then use a fallback default value.

    Optionally if reject_negative is True, then it will fallback
    to the default value if the user specified is negative.

    :param arg_name:
    :param default_value:
    :param reject_negative:
    :return:
    """

    # Get the query argument in string form
    n_str: str = request.args.get(arg_name, default=default_value)

    try:
        # Attempt to convert to a python int
        n: int = int(n_str)

        # If reject_negative, then check if
        # the parsed value is negative.
        if reject_negative and n < 0:
            # If it was negative, then fallback to default
            return default_value

        # Return integer value
        return n
    except ValueError:
        # ValueError is raised if the string to int
        # conversion was unsuccessful. In that case,
        # then we fallback to default
        return default_value


def get_request_file_stream(with_filename=False) -> Union[bytes, None, Tuple[bytes, str]]:
    """
    Get first file uploaded in the request. Will return None if
    there is no file uploaded.

    :return:
    """

    # Check to see if we have a single file
    if len(request.files) != 1:
        return None

    # Get file from request
    file = list(request.files.values())[0]

    # If they want the filename too
    if with_filename:
        return file.stream.read(), file.filename

    # Read its stream
    return file.stream.read()


def get_request_days_offset():
    """
    From the days and offset values specified in GET query, construct
    datetime objects for the start and end time.

    :return:
    """
    days = get_number_arg("days", default_value=100)
    offset = get_number_arg("offset", default_value=0)

    start_time = datetime.utcnow() - timedelta(days=offset + days)
    end_time = start_time + timedelta(days=days)

    return start_time, end_time
