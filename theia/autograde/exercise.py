import re
import os

from models import FileSystemState, FileSystemCondition, Exercise, UserState
from utils import RejectionException

exercises: dict[str, Exercise] = {
    'helloworld':       Exercise(
        name='helloworld',
        command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"?'),
        output_regex=re.compile(r'[Hh]ello\s[Ww]orld!?'),
    ),
    'mkdir':            Exercise(
        name='mkdir exercise1',
        requires_exercises=['helloworld'],
        command_regex=re.compile(r'mkdir \'?"?exercise1?\'?"?'),
        filesystem_conditions=[
            FileSystemCondition(
                path='exercise1',
                directory=True,
                state=FileSystemState.PRESENT,
            )
        ]
    ),
    'pipe hello world': Exercise(
        name='pipe hello world',
        requires_exercises=['mkdir'],
        command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"? > exercise.txt'),
        filesystem_conditions=[
            FileSystemCondition(
                path='exercise1/exercise.txt',
                state=FileSystemState.PRESENT,
                content_regex=re.compile(r'[Hh]ello\s[Ww]orld!')
            )
        ]
    ),
}


def verify_exercise(user_state: UserState) -> Exercise:
    exercise = exercises.get(user_state.exercise_name, None)
    if exercise is None:
        raise RejectionException('Exercise not found!')
    return exercise


def verify_required(exercise: Exercise, _: UserState):
    # Verify required exercises complete
    if exercise.requires_exercises is None:
        return

    for requires_exercise_name in exercise.requires_exercises:
        requires_exercise = exercises[requires_exercise_name]
        if not requires_exercise.complete:
            raise RejectionException(f'Required exercise not complete: {requires_exercise.name}')


def verify_command_regex(exercise: Exercise, user_state: UserState):
    # Check command against regex
    if exercise.command_regex is None:
        return

    command_match = exercise.command_regex.match(user_state.command)
    if command_match is None:
        raise RejectionException('Sorry your command does not seem right.')


def verify_output_regex(exercise: Exercise, user_state: UserState):
    # Check output against regex
    if exercise.output_regex is None:
        return

    output_match = exercise.output_regex.match(user_state.output)
    if output_match is None:
        raise RejectionException('Sorry your output does not seem right.')


def verify_filesystem_conditions(exercise: Exercise, user_state: UserState):
    if exercise.filesystem_conditions is None:
        return

    for filesystem_condition in exercise.filesystem_conditions:
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


