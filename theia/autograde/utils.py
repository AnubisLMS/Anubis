import functools

from flask import Response, make_response, request

from models import UserState


def user_state_from_request() -> UserState:
    user_exercise_name: str = request.form.get('exercise', default='').strip()
    user_command: str = request.form.get('command', default='')
    user_output: str = request.form.get('output', default='')
    user_cwd: str = request.form.get('cwd', default='/home/anubis')

    user_state = UserState(
        exercise_name=user_exercise_name,
        command=user_command,
        output=user_output,
        cwd=user_cwd,
    )

    return user_state


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
