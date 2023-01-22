import pytest

from anubis_autograde.exercise.init import set_exercises
from anubis_autograde.exercise.get import get_active_exercise
from anubis_autograde.exercise.verify import run_exercise
from anubis_autograde.models import Exercise, UserState
from dataclasses import asdict, dataclass

@dataclass
class Response:
    exercise: str
    command: str = ''
    output: str = ''
    cwd: str = '/home/anubis'
    env: str = ''

def eject_with_raise(_, __):
    raise RuntimeError('AAAAAAAAAAA')


def eject_without_raise(_, __):
    pass


def eject_success(_, __):
    return True


def eject_failure(_, __):
    return False


class TestExerciseVerify:
    @pytest.mark.parametrize("eject_func,complete", [
        (eject_with_raise, False),
        (eject_without_raise, False),
        (eject_success, True),
        (eject_failure, False),
    ])
    def test_eject(self, client, eject_func, complete):
        start_exercise_name = 'start placeholder'
        eject_exercise_name = str(eject_func.__name__)
        set_exercises([
            Exercise(name='start placeholder'),
            Exercise(name=eject_exercise_name, eject_function=eject_func)
        ], 'start', 'end')

        user_state = Response(start_exercise_name, start_exercise_name)
        r = client.post('/submit', data=asdict(user_state))
        assert r.status_code == 200

        assert get_active_exercise()[1].name == eject_exercise_name
        user_state.exercise = eject_exercise_name
        user_state.command = eject_exercise_name
        r = client.post('/submit', data=asdict(user_state))

        if complete:
            assert r.status_code == 200
            assert 'Congrats' in r.text
        else:
            assert r.status_code == 406
            assert 'Sorry' in r.text
