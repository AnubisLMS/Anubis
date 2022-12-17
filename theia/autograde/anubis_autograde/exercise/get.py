import base64
import binascii
import traceback
import typing

from flask import request

from anubis_autograde.logging import log
from anubis_autograde.models import Exercise, UserState
from anubis_autograde.utils import colorize_render
from anubis_autograde.utils import remove_unprintable

_start_message: typing.Optional[str] = None
_end_message: typing.Optional[str] = None
_exercises: typing.Optional[typing.List[Exercise]] = None


def get_active_exercise() -> typing.Tuple[int, typing.Optional[Exercise]]:
    for index, exercise in enumerate(_exercises):
        if not exercise.complete:
            return index, exercise
    return -1, None


def get_active_exercise_hint() -> str:
    _, current_exercise = get_active_exercise()
    if current_exercise.hint_message is None:
        return colorize_render(f'Exercise Hint: {current_exercise.hint_message}', termcolor_args=("yellow",))
    return colorize_render(f'Exercise Hint: {current_exercise.hint_message}', termcolor_args=("yellow",))


def get_exercises() -> typing.List[Exercise]:
    return _exercises or []


def get_start_message() -> str:
    if _start_message is None:
        return ''
    return colorize_render(_start_message)


def get_end_message() -> str:
    if _end_message is None:
        return ''
    return colorize_render(_end_message, termcolor_args=("yellow",))


def set_exercises(
    exercises: typing.List[Exercise],
    start_message: str,
    end_message: str,
) -> typing.Tuple[typing.List[Exercise], str, str]:
    global _exercises, _start_message, _end_message
    _exercises = exercises
    _start_message = start_message
    _end_message = end_message
    return _exercises, _start_message, _end_message


def reset_exercises() -> int:
    for exercise in _exercises:
        exercise.complete = False
    return 0


def is_all_complete() -> bool:
    return all(map(lambda exercise: exercise.complete, _exercises))


def _parse_user_env(user_env: str) -> typing.Dict[str, str]:
    try:
        decoded: bytes = base64.b64decode(user_env.replace('\n', ''))
    except binascii.Error:
        log.error(f'{traceback.format_exc()}\nuser_env={user_env}\nUnable to parse user_env')
        return dict()

    decoded: str = remove_unprintable(decoded)

    env_vars = dict()
    for line in decoded.splitlines():
        if len(line) == 0:
            continue

        try:
            equals = line.index('=')
        except ValueError:
            log.warning(f'Could not parse env line line={line}')
            continue

        name = line[0:equals]
        value = line[equals + 1:]

        env_vars[name] = value

    return env_vars


def get_user_state() -> UserState:
    user_exercise_name: str = request.form.get('exercise', default='').strip()
    user_command: str = request.form.get('command', default='')
    user_output: str = request.form.get('output', default='')
    user_cwd: str = request.form.get('cwd', default='/home/anubis')  # TODO verify valid path before this reached prod
    user_env: str = request.form.get('env', default='')

    user_state = UserState(
        exercise_name=user_exercise_name,
        command=user_command,
        output=user_output,
        cwd=user_cwd,
        environ=_parse_user_env(user_env)
    )

    return user_state
