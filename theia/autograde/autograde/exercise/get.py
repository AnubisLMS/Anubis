from autograde.models import Exercise

_exercises: list[Exercise] | None = None


def get_exercises() -> list[Exercise]:
    return _exercises

def set_exercises(exercises: list[Exercise]) -> list[Exercise]:
    global _exercises
    _exercises = exercises
    return _exercises
