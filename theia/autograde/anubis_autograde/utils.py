import functools
import glob
import os
import string
import typing

import jinja2
from flask import Response, make_response, current_app
from termcolor import colored as _colored

from anubis_autograde.exceptions import RejectionException


def expand_path(path: str) -> str:
    path = os.path.expanduser(path)
    paths = glob.glob(path, recursive=True)
    if len(paths) >= 1:
        return paths[0]
    return path


def remove_unprintable(s: typing.Union[str, bytes]) -> str:
    valid: set[int] = set(ord(c) for c in string.printable)
    ss: list[str] = []
    for c in s:
        if isinstance(c, int) and c in valid:
            ss.append(chr(c))
        elif isinstance(c, str) and ord(c) in valid:
            ss.append(c)
    return ''.join(ss)

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
    def wrapper(*args, **kwargs) -> typing.Union[Response, typing.Tuple[str, int]]:
        try:
            return func(*args, **kwargs)
        except RejectionException as e:
            msg = e.msg

            from anubis_autograde.exercise.get import get_active_exercise, get_start_message, get_active_exercise_hint
            _, current_exercise = get_active_exercise()
            current_exercise.failures += 1
            if current_exercise.failures > current_exercise.fail_to_assignment_start_message_count and get_start_message() is not None:
                msg += '\n' + get_start_message()
            if current_exercise.failures > current_exercise.fail_to_exercise_start_message_count and current_exercise.start_message is not None:
                msg += '\n' + colorize_render(current_exercise.start_message)
            if current_exercise.failures > current_exercise.fail_to_hint_message_count and current_exercise.hint_message is not None:
                msg += '\n' + get_active_exercise_hint()

            return msg, e.status_code

    return wrapper


def complete_reject(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> typing.Union[Response, typing.Tuple[str, int]]:
        from anubis_autograde.exercise.get import is_all_complete
        if is_all_complete():
            return f'This assignment is complete. ' \
                   f'You can use the reset command to replay.', 200
        return func(*args, **kwargs)

    return wrapper


def skip_if_debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.debug:
            return
        return func(*args, **kwargs)

    return wrapper


def colorize_render(
    s: str,
    termcolor_args: tuple = ('cyan',),
    **kwargs
) -> str:
    colored = _colored(s, *termcolor_args)
    return jinja2.Template(colored).render(**kwargs)
