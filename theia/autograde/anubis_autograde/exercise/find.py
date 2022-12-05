import typing

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.models import Exercise


def find_exercise(name: str) -> typing.Tuple[typing.Optional[Exercise], int]:
    for index, exercise in enumerate(get_exercises()):
        if exercise.name == name:
            return exercise, index
    else:
        return None, -1
