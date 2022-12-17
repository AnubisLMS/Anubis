import argparse

import flask
import pytest
from anubis_autograde.server.run import create_app
from anubis_autograde.parser import make_parser

pytest_plugins = "pytester"


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    return make_parser()


@pytest.fixture()
def app(parser) -> flask.Flask:
    args = parser.parse_args(['--debug', 'server', 'exercise.py'])
    _app = create_app(args, skip_exercises=True)
    _app.config.update({
        'TESTING': True,
    })
    yield _app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

