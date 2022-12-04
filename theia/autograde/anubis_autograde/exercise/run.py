import argparse
import datetime

import jinja2

exercise_template = jinja2.Template("""
# Anubis Live Shell Assignment
# Generated: {{ now }}
# See documentation at https://anubis-lms.io/autograde/

import re

from anubis_autograde.models import Exercise, FileSystemCondition, ExistState

start_message: str = '''echo hello world
mkdir exercise1
cd exercise1
echo hello world > exercise.txt'''

end_message: str = '''Congratulations! You have finished this assignment. '''

exercises: list[Exercise] = [
    Exercise(
        name='helloworld',
        hint_message='\\ntype: echo "hello world"',
        command_regex=re.compile(r'echo \\'?"?[Hh]ello\\s[Ww]orld!?\\'?"?'),
        output_regex=re.compile(r'[Hh]ello\\s[Ww]orld!?'),
    ),
    Exercise(
        name='mkdir exercise1',
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
        command_regex=re.compile(r'cd \\'?"?exercise1\\'?"?'),
    ),
    Exercise(
        name='pipe hello world',
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
