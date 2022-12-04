from autograde.exercise.get import get_exercises
from autograde.models import Exercise


def find_exercise(name: str) -> tuple[Exercise| None, int]:
    for index, exercise in enumerate(get_exercises()):
        if exercise.name == name:
            return exercise, index
    else:
        return None, -1
