import argparse
import traceback

from anubis_autograde.exercise.get import set_exercises
from anubis_autograde.logging import log


def init_exercises(args: argparse.Namespace):
    try:
        module_name = args.exercise_module.removesuffix('.py')
        exercise_module = __import__(module_name)
    except Exception as e:
        log.error(traceback.format_exc())
        log.error(f'Failed to import exercise module {e=}')
        exit(1)

    try:
        exercises = set_exercises(exercise_module.exercises)
    except Exception as e:
        log.error(traceback.format_exc())
        log.error(f'Failed to import exercise module {e=}')
        exit(1)

    log.info(f'loaded exercises {exercises=}')
