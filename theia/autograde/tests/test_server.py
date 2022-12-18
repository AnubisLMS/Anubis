from dataclasses import asdict, dataclass
from pathlib import Path

import pytest
from werkzeug.test import TestResponse

from anubis_autograde.exercise.get import get_active_exercise


@dataclass
class Response:
    exercise: str
    command: str
    output: str
    cwd: str
    env: str = ''

    dir_: Path = None
    file_: dict[Path, str] = None


@pytest.fixture()
def sample_answers(pytester, exercise):
    return [
        Response(
            exercise.exercises[0].name,
            exercise.exercises[0].hint_message,
            'Hello World',
            str(pytester.path),
        ),
        Response(
            exercise.exercises[1].name,
            exercise.exercises[1].hint_message,
            '',
            str(pytester.path),
            dir_=pytester.path / 'exercise1',
        ),
        Response(
            exercise.exercises[2].name,
            exercise.exercises[2].hint_message,
            '',
            str(pytester.path / 'exercise1'),
        ),
        Response(
            exercise.exercises[3].name,
            exercise.exercises[3].hint_message,
            '',
            str(pytester.path / 'exercise1'),
            file_={pytester.path / 'exercise1' / 'exercise.txt': 'Hello World'}
        ),
    ]


def _submit(request, client, exercise, sample_answers) -> int:
    for i in range(request.param + 1):
        # Create dirs if necessary
        if sample_answers[i].dir_:
            sample_answers[i].dir_.mkdir(exist_ok=True)
            sample_answers[i].dir_ = None

        # Create files if necessary
        if sample_answers[i].file_:
            for file, content in sample_answers[i].file_.items():
                file.write_text(content)
            sample_answers[i].file_ = None

        # Make sure cwd exists
        Path(sample_answers[i].cwd).mkdir(exist_ok=True)
        response: TestResponse = client.post('/submit', data=asdict(sample_answers[i]))
        assert 'Congrats!' in response.text
        if i == len(sample_answers) - 1:
            assert exercise.end_message in response.text
            assert get_active_exercise()[0] == -1
        else:
            assert get_active_exercise()[0] == i + 1
    return request.param


@pytest.fixture(params=[0, 1, 2])  # , pytest.param(3, marks=pytest.mark.skip)
def submit(pytester, request, client, exercise, sample_answers) -> int:
    return _submit(request, client, exercise, sample_answers)


@pytest.fixture(params=[3])
def complete(pytester, request, client, exercise, sample_answers) -> int:
    return _submit(request, client, exercise, sample_answers)


@pytest.fixture(params=range(20))
def submit_wrong(pytester, request, client, exercise, sample_answers):
    answer = asdict(sample_answers[0])
    answer['command'] = 'echo wrong'

    for i in range(request.param):
        response: TestResponse = client.post('/submit', data=answer)
        assert response.status_code == 406
        assert 'Sorry your command does not seem right.' in response.text

        if i >= exercise.exercises[0].fail_to_hint_message_count:
            assert exercise.exercises[0].hint_message in response.text
        if i >= exercise.exercises[0].fail_to_exercise_start_message_count:
            assert exercise.exercises[0].start_message in response.text
        if i >= exercise.exercises[0].fail_to_assignment_start_message_count:
            assert exercise.start_message in response.text

class TestServer:
    def test_status(self, exercise, client):
        response: TestResponse = client.get('/status')
        assert "\x1b[5m\x1b[36m->\x1b[0m helloworld" in response.text

    def test_reset(self, submit, exercise, client):
        response: TestResponse = client.get('/status')
        assert f'\x1b[5m\x1b[36m->\x1b[0m {exercise.exercises[submit + 1].name}' in response.text

        response: TestResponse = client.get('/reset')
        assert response.status_code == 200

        response: TestResponse = client.get('/status')
        assert f'\x1b[5m\x1b[36m->\x1b[0m {exercise.exercises[0].name}' in response.text

    def test_hint(self, exercise, client):
        response: TestResponse = client.get('/hint')
        assert exercise.exercises[0].hint_message in response.text

    def test_start(self, exercise, client):
        response: TestResponse = client.get('/start')
        assert exercise.start_message in response.text

    def test_submit(self, submit):
        pass

    def test_server_complete(self, complete):
        pass

    def test_submit_wrong(self, submit_wrong):
        pass
