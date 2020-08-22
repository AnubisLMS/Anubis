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
