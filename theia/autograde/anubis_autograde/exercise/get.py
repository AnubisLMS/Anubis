import base64
import binascii
import traceback

from flask import request

from anubis_autograde.logging import log
from anubis_autograde.models import Exercise, UserState
from anubis_autograde.utils import remove_unprintable

_exercises: list[Exercise] | None = None


def get_exercises() -> list[Exercise]:
    return _exercises


def set_exercises(exercises: list[Exercise]) -> list[Exercise]:
    global _exercises
    _exercises = exercises
    return _exercises


def _parse_user_env(user_env: str) -> dict[str, str]:
    try:
        decoded = base64.b64decode(user_env)
    except binascii.Error:
        log.error(f'{traceback.format_exc()}\n{user_env=}\nUnable to parse user_env')
        return dict()

    decoded: str = remove_unprintable(decoded)

    env_vars = dict()
    for line in decoded.splitlines():
        if len(line) == 0:
            continue

        try:
            equals = line.index('=')
        except ValueError:
            log.warning(f'Could not parse env line {line=}')
            continue

        name = line[0:equals]
        value = line[equals + 1:]

        env_vars[name] = value

    return env_vars


def get_user_state() -> UserState:
    user_exercise_name: str = request.form.get('exercise', default='').strip()
    user_command: str = request.form.get('command', default='')
    user_output: str = request.form.get('output', default='')
    user_cwd: str = request.form.get('cwd', default='/home/anubis')
    user_env: str = request.form.get('env', default='')

    user_state = UserState(
        exercise_name=user_exercise_name,
        command=user_command,
        output=user_output,
        cwd=user_cwd,
        environ=_parse_user_env(user_env)
    )

    return user_state
