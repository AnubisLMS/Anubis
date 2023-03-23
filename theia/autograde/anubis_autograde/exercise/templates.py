import jinja2

exercise_template = jinja2.Template("""
# Anubis Live Shell Assignment
# Generated: {{ now }}
# See documentation at https://anubis-lms.io/autograde/

import re
import typing

from anubis_autograde.models import Exercise, FileSystemCondition, ExistState

start_message: str = '''Welcome to the Hello World assignment!'''

end_message: str = '''Congratulations! You have finished this assignment.'''

exercises: typing.List[Exercise] = [
    Exercise(
        name='helloworld',
        start_message='Write a command to print out hello \"world\"',
        hint_message='echo "hello world"',
        command_regex=re.compile(r'echo \\'?"?[Hh]ello\\s[Ww]orld!?\\'?"?'),
        output_regex=re.compile(r'[Hh]ello\\s[Ww]orld!?'),
    ),
    Exercise(
        name='mkdir exercise1',
        start_message='Create a \"exercise1\" directory',
        hint_message='mkdir exercise1',
        filesystem_conditions=[
            FileSystemCondition(
                path='exercise1',
                state=ExistState.PRESENT,
                state_fail_message='Try creating the exercise1 directory with the mkdir command',
                directory=True,
                directory_fail_message='Try creating a directory instead of a file',
            )
        ]
    ),
    Exercise(
        name='cd exercise1',
        start_message='Change directory into the exercise1 directory',
        hint_message='cd exercise1',
        command_regex=re.compile(r'cd \\'?"?exercise1\\'?"?'),
    ),
    Exercise(
        name='pipe hello world',
        start_message='Use the print command from earlier to pipe \"hello world\" into a file \"exercise.txt\"',
        hint_message='echo hello world > exercise.txt',
        command_regex=re.compile(r'echo \\'?"?[Hh]ello\\s[Ww]orld!?\\'?"? > exercise.txt'),
        cwd_regex=re.compile(r'.*/exercise1$'),
        filesystem_conditions=[
            FileSystemCondition(
                path='exercise.txt',
                state=ExistState.PRESENT,
                content_regex=re.compile(r'[Hh]ello\\s[Ww]orld!?')
            )
        ]
    ),
]


def init():
    \"\"\"
    This function is called when the exercise is initialized, and when 
    the reset function is typed by the student. It is *not* called when
    the an assignment IDE is resumed from a previous submission.
    
    This is where you should park any and all of your initialization logic 
    for the assignment. Drop files, clear directories it is all up to you.
    
    Be careful to write resilient code here.  
    \"\"\"
    pass
"""
)
