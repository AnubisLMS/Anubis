import os
import traceback
import typing

from flask import current_app

from anubis_autograde.exercise.find import find_exercise
from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.logging import log
from anubis_autograde.models import UserState, Exercise, FileSystemCondition, ExistState, EnvVarCondition
from anubis_autograde.utils import expand_path, colorize_render
from anubis_autograde.exceptions import RejectionException
from anubis_autograde.exercise.pipeline import forward_exercise_status


def _r(
    exercise: Exercise,
    user_state: UserState,
    condition: str,
    default_message: str,
    item: typing.Union[Exercise, FileSystemCondition, EnvVarCondition] = None
):
    """
    :param exercise: current exercise
    :param user_state: current user state
    :param condition: string describing condition that was failed (eg: "command_regex")
    :param default_message: default message for fail condition
    :param item: item within exercise that failed. this could be the exercise, or a filesystem condition, etc...
    :return:
    """

    if item is None:
        item = exercise

    exercise_fail_message: str | None = getattr(item, f'{condition}_fail_message') or getattr(item, 'fail_message')
    if exercise_fail_message is None:
        raise RejectionException(default_message)

    raise RejectionException(colorize_render(
        exercise_fail_message,
        exercise=exercise,
        user_state=user_state,
        condition=condition,
    ))


def verify_exercise(user_state: UserState) -> Exercise:
    exercise, _ = find_exercise(user_state.exercise_name)
    if exercise is None:
        raise RejectionException('Exercise not found!')
    return exercise


def verify_required(exercise: Exercise, _: UserState):
    _, index = find_exercise(exercise.name)
    exercises = get_exercises()

    for required_exercise_index in range(index):
        required_exercise = exercises[required_exercise_index]
        if not required_exercise.complete:
            raise RejectionException(f'Required exercise not complete: {required_exercise.name}')


def verify_command_regex(exercise: Exercise, user_state: UserState):
    # Check command against regex
    if exercise.command_regex is None:
        return

    log.info(f'exercise.command_regex = {exercise.command_regex}')

    command_match = exercise.command_regex.match(user_state.command)
    if command_match is None:
        raise _r(exercise, user_state, 'command_regex', 'Sorry your command does not seem right.')


def verify_cwd_regex(exercise: Exercise, user_state: UserState):
    # Check cwd against regex
    if exercise.cwd_regex is None:
        return

    log.info(f'exercise.cwd_regex = {exercise.cwd_regex}')

    cwd_match = exercise.cwd_regex.match(user_state.cwd)
    if cwd_match is None:
        raise _r(exercise, user_state, 'cwd_regex', 'Sorry your current working directory does not seem right.')


def verify_output_regex(exercise: Exercise, user_state: UserState):
    # Check output against regex
    if exercise.output_regex is None:
        return

    log.info(f'exercise.command_regex = {exercise.command_regex}')

    output_match = exercise.output_regex.match(user_state.output)
    if output_match is None:
        raise _r(exercise, user_state, 'output_regex', 'Sorry your output does not seem right.')


def verify_filesystem_conditions(exercise: Exercise, user_state: UserState):
    if exercise.filesystem_conditions is None:
        return

    for filesystem_condition in exercise.filesystem_conditions:
        filesystem_condition: FileSystemCondition
        path = expand_path(filesystem_condition.path)

        if not path.startswith('/'):
            path = os.path.join(user_state.cwd, path)

        debug = current_app.debug

        if not debug and (
            (not path.startswith('/home/anubis/')) or
            ('..' in path)
        ):
            raise RejectionException('Current working dir not allowed')

        exists = os.path.exists(path)
        isdir = os.path.isdir(path)

        # Check State
        if filesystem_condition.state == ExistState.PRESENT and not exists:
            raise _r(exercise, user_state, 'state', f'File or Directory: {path} should exist', filesystem_condition)
        if filesystem_condition.state != ExistState.PRESENT and exists:
            raise _r(exercise, user_state, 'state', f'File or Directory: {path} should not exist', filesystem_condition)

        # Check directory
        if filesystem_condition.directory and not isdir:
            raise _r(exercise, user_state, 'directory', f'File: {path} should be a directory', filesystem_condition)
        if not filesystem_condition.directory and isdir:
            raise _r(exercise, user_state, 'directory', f'Directory: {path} should be a file', filesystem_condition)

        # Check content
        if filesystem_condition.content is not None:
            with open(path, 'r') as f:
                content = f.read()
                if content != filesystem_condition.content:
                    raise _r(exercise, user_state, 'content', f'File: {path} does not match expected content',
                             filesystem_condition)

        # Check content regex
        if filesystem_condition.content_regex is not None:
            with open(path, 'r') as f:
                content = f.read()
                content_match = filesystem_condition.content_regex.match(content)
                if content_match is None:
                    raise _r(exercise, user_state, 'content_regex', f'File: {path} does not match expected content',
                             filesystem_condition)


def verify_env_var_conditions(exercise: Exercise, user_state: UserState):
    if exercise.env_var_conditions is None:
        return

    for env_var_condition in exercise.env_var_conditions:
        env_var_condition: EnvVarCondition

        name = env_var_condition.name
        value = user_state.environ.get(name, None)
        exists = value is not None

        if env_var_condition.state == ExistState.ABSENT and exists:
            raise _r(exercise, user_state, 'state', f'Environment Variable: "{name}" should not be set',
                     env_var_condition)
        if env_var_condition.state == ExistState.PRESENT and not exists:
            raise _r(exercise, user_state, 'state', f'Environment Variable: "{name}" should be set',
                     env_var_condition)

        if env_var_condition.value_regex is not None:
            value_match = env_var_condition.value_regex.match(value)
            if value_match is None:
                raise _r(exercise, user_state, 'value_regex',
                         f'Environment Variable: "{name}" does not match expected value', env_var_condition)


def run_eject_function(exercise: Exercise, user_state: UserState):
    log.info(f'Running eject function for exercise={exercise} user_state={user_state}')
    try:
        complete = exercise.eject_function(exercise, user_state)

        # Verify that the return value for the eject function is actually a bool
        if not isinstance(complete, bool):
            log.error(f'return of eject_function for {exercise.name} was not bool complete={complete}')
            return

        exercise.complete = complete
    except Exception:
        log.error(f'{traceback.format_exc()}\neject_function for {exercise.name} threw error')


def run_exercise(user_state: UserState) -> Exercise:
    exercise = verify_exercise(user_state)

    # Log
    log.info(f'exercise = {exercise}')
    log.info(f'user_state = {user_state}')

    # Make sure previous exercises are complete
    verify_required(exercise, user_state)

    # If eject function specified, then run that and return
    if exercise.eject_function is not None:
        run_eject_function(exercise, user_state)
        return exercise

    verify_command_regex(exercise, user_state)
    verify_output_regex(exercise, user_state)
    verify_cwd_regex(exercise, user_state)
    verify_filesystem_conditions(exercise, user_state)
    verify_env_var_conditions(exercise, user_state)

    exercise.complete = True

    forward_exercise_status(exercise, user_state)

    return exercise
