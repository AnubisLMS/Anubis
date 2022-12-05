import argparse
import datetime

import jinja2

exercise_template = jinja2.Template("""
# Anubis Live Shell Assignment
# Generated: {{ now }}
# See documentation at https://anubis-lms.io/autograde/

import re

from anubis_autograde.models import Exercise, FileSystemCondition, ExistState

start_message: str = ''''''

end_message: str = '''Congratulations! You have finished this assignment.'''

exercises: list[Exercise] = [
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
        command_regex=re.compile(r'mkdir \\'?"?exercise1?\\'?"?'),
        filesystem_conditions=[
            FileSystemCondition(
                path='exercise1',
                directory=True,
                state=ExistState.PRESENT,
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
""")


def run_exercise_init(_: argparse.Namespace):
    now = datetime.datetime.now()
    exercise = exercise_template.render(now=now)
    with open('exercise.py', 'w') as f:
        f.write(exercise)
