import argparse
import os
from pathlib import Path

import pytest
from flask import Flask

from anubis_autograde.exercise.run import run_exercise_init
from anubis_autograde.parser import make_parser
from anubis_autograde.server.run import create_app

pytest_plugins = "pytester"


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    return make_parser()


@pytest.fixture()
def exercise_py(pytester, parser) -> Path:
    args = ['exercise-init']
    args = parser.parse_args(args)
    run_exercise_init(args)
    exercise_py = (pytester.path / 'exercise.py')
    assert exercise_py.exists()
    return exercise_py


@pytest.fixture()
def exercise(exercise_py):
    os.chdir(exercise_py.parent)
    import exercise
    assert exercise
    return exercise


@pytest.fixture()
def app(parser, exercise) -> Flask:
    args = parser.parse_args(['--debug', 'server', 'exercise.py'])
    _app = create_app(args)
    _app.config.update({
        'TESTING': True,
        'DEBUG':   True,
    })
    yield _app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
