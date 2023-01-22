import argparse
import datetime

from anubis_autograde.exercise.templates import exercise_template


def run_exercise_init(_: argparse.Namespace):
    now = datetime.datetime.now()
    exercise = exercise_template.render(now=now)
    with open('exercise.py', 'w') as f:
        f.write(exercise)
