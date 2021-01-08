from datetime import datetime, timedelta
from typing import Union

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
        return request.headers[
            header
        ] if header in request.headers else ''

    def check_(headers, n=0):
        """check headers based on ordered piority"""
        if n == len(headers):
            return ''
        return check(headers[n]) or check_(headers, n + 1)

    return str(check_([
        'x-forwarded-for',  # highest priority
        'X-Forwarded-For',
        'x-real-ip',
        'X-Real-Ip',  # lowest priority
    ]) or request.remote_addr or 'N/A')


def error_response(error_message: str) -> dict:
    """
    Form an error REST api response dict.

    :param error_message: string error message
    :return:
    """
    return {
        'success': False,
        'error': error_message,
        'data': None,
    }


def success_response(data: Union[dict, str, None]) -> dict:
    """
    Form a success REST api response dict.

    :param data:
    :return:
    """
    return {
        'success': True,
        'error': None,
        'data': data,
    }


def get_number_arg(arg_name: str = "number", default_value: int = 10) -> int:
    n = request.args.get(arg_name, default=default_value)
    try:
        return int(n)
    except ValueError:
        return default_value


def get_request_file_stream() -> Union[bytes, None]:
    """
    Get first file uploaded in the request. Will return None if
    there is no file uploaded.

    :return:
    """

    # Check to see if we have a single file
    if len(request.files) != 1:
        return None

    # Read its stream
    return list(request.files.values())[0].stream.read()


def get_request_days_offset():
    """
    From the days and offset values specified in GET query, construct
    datetime objects for the start and end time.

    :return:
    """
    days = get_number_arg('days', default_value=100)
    offset = get_number_arg('offset', default_value=0)

    start_time = datetime.utcnow() - timedelta(days=offset + days)
    end_time = start_time + timedelta(days=days)

    return start_time, end_time
