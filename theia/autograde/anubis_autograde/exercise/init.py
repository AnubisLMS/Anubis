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
        exercises, start_message, end_message = set_exercises(
            exercise_module.exercises,
            exercise_module.start_message,
            exercise_module.end_message,
        )
    except Exception as e:
        log.error(traceback.format_exc())
        log.error(f'Failed to import exercise module {e=}')
        exit(1)

    log.info(f'loaded exercises {exercises=}')
    log.debug(f'{start_message=}')
    log.debug(f'{end_message=}')
