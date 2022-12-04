import os
import traceback

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.exercise.find import find_exercise
from anubis_autograde.logging import log
from anubis_autograde.models import UserState, Exercise, FileSystemCondition, FileSystemState
from anubis_autograde.utils import RejectionException


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
        raise RejectionException('Sorry your command does not seem right.')


def verify_output_regex(exercise: Exercise, user_state: UserState):
    # Check output against regex
    if exercise.output_regex is None:
        return

    log.info(f'exercise.command_regex = {exercise.command_regex}')

    output_match = exercise.output_regex.match(user_state.output)
    if output_match is None:
        raise RejectionException('Sorry your output does not seem right.')


def verify_filesystem_conditions(exercise: Exercise, _: UserState):
    if exercise.filesystem_conditions is None:
        return

    for filesystem_condition in exercise.filesystem_conditions:
        filesystem_condition: FileSystemCondition
        path = os.path.join('/home/anubis', filesystem_condition.path)
        exists = os.path.exists(path)
        isdir = os.path.isdir(path)

        # Check State
        if filesystem_condition.state == FileSystemState.PRESENT and not exists:
            raise RejectionException(f'File or Directory: {path} should exist')
        if filesystem_condition.state != FileSystemState.PRESENT and exists:
            raise RejectionException(f'File or Directory: {path} should not exist')

        # Check directory
        if filesystem_condition.directory and not isdir:
            raise RejectionException(f'File: {path} should be a directory')
        if not filesystem_condition.directory and isdir:
            raise RejectionException(f'Directory: {path} should be a file')

        # Check content
        if filesystem_condition.content is not None:
            with open(path, 'r') as f:
                content = f.read()
                if content != filesystem_condition.content:
                    raise RejectionException(f'File: {path} does not match expected content')

        # Check content regex
        if filesystem_condition.content_regex is not None:
            with open(path, 'r') as f:
                content = f.read()
                content_match = filesystem_condition.content_regex.match(content)
                if content_match is None:
                    raise RejectionException(f'File: {path} does not match expected content')


def verify_env_var_conditions(exercise: Exercise, user_state: UserState):
    pass


def run_eject_function(exercise: Exercise, user_state: UserState):
    log.info(f'Running eject function for {exercise=} {user_state=}')
    try:
        complete = exercise.eject_function(exercise, user_state)

        # Verify that the return value for the eject function is actually a bool
        if not isinstance(complete, bool):
            log.error(f'return of eject_function for {exercise.name} was not bool {complete=}')
            return

        exercise.complete = complete
    except Exception:
        log.error(f'{traceback.format_exc()}\neject_function for {exercise.name} threw error')


def run_exercise(user_state: UserState) -> Exercise:
    exercise = verify_exercise(user_state)
    verify_required(exercise, user_state)

    # If eject function specified, then run that and return
    if exercise.eject_function is not None:
        run_eject_function(exercise, user_state)
        return exercise

    verify_command_regex(exercise, user_state)
    verify_output_regex(exercise, user_state)
    verify_filesystem_conditions(exercise, user_state)

    exercise.complete = True

    return exercise
