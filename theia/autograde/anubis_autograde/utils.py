import functools
import string

from flask import Response, make_response


def remove_unprintable(s: str | bytes) -> str:
    valid: set[int] = set(ord(c) for c in string.printable)
    return ''.join(chr(c) for c in s if (c if isinstance(c, int) else ord(c)) in valid)


def text_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        r = func(*args, **kwargs)

        if not isinstance(r, tuple):
            message: str = r
            status_code: int = 200
        else:
            message, status_code = r

        r = make_response(message + '\n')
        r.status_code = status_code
        r.headers['Content-Type'] = 'text/plain'
        return r

    return wrapper


def reject_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response | tuple[str, int]:
        try:
            return func(*args, **kwargs)
        except RejectionException as e:
            return e.msg, e.status_code

    return wrapper


class RejectionException(Exception):
    def __init__(self, msg: str, status_code: int = 406):
        self.msg = msg
        self.status_code = status_code
        super(RejectionException, self).__init__(msg)
