import argparse
import os
import traceback


from autograde.logging import log
from autograde.models import FileSystemState, FileSystemCondition, Exercise, UserState
from autograde.utils import RejectionException

_exercises: list[Exercise] | None = None


def get_exercises() -> list[Exercise]:
    return _exercises


def init_exercises(args: argparse.Namespace):
    global _exercises

    try:
        module_name = args.exercise_module.removesuffix('.py')
        exercise_module = __import__(module_name)
    except Exception as e:
        log.error(traceback.format_exc())
        log.error(f'Failed to import exercise module {e=}')
        exit(1)

    try:
        _exercises = exercise_module._exercises
    except Exception as e:
        log.error(traceback.format_exc())
        log.error(f'Failed to import exercise module {e=}')
        exit(1)

    log.info(f'loaded exercises {_exercises=}')


def find_exercise(name: str) -> tuple[Exercise| None, int]:
    for index, exercise in enumerate(_exercises):
        if exercise.name == name:
            return exercise, index
    else:
        return None, -1


def verify_exercise(user_state: UserState) -> Exercise:
    exercise, _ = find_exercise(user_state.exercise_name)
    if exercise is None:
        raise RejectionException('Exercise not found!')
    return exercise


def verify_required(exercise: Exercise, _: UserState):
    _, index = find_exercise(exercise.name)

    for required_exercise_index in range(index):
        required_exercise = _exercises[required_exercise_index]
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


def run_exercise(user_state: UserState) -> Exercise:
    exercise = verify_exercise(user_state)

    verify_required(exercise, user_state)
    verify_command_regex(exercise, user_state)
    verify_output_regex(exercise, user_state)
    verify_filesystem_conditions(exercise, user_state)

    exercise.complete = True

    return Exercise
