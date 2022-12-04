#!/usr/bin/python3
import argparse
import logging

import gunicorn.app.base
from flask import Flask

from autograde.exercise import run_exercise, init_exercises, get_exercises
from autograde.utils import text_response, reject_handler, user_state_from_request
from autograde.shell import init_bashrc

app = Flask(__name__)


def init_logging():
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def run_server(args: argparse.Namespace):
    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, _app, options=None):
            self.options = options or {}
            self.application = _app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    init_logging()
    init_exercises(args)
    init_bashrc(args)
    StandaloneApplication(app, options={
        'bind':                     args.bind,
        'workers':                  1,
        'capture-output':           True,
        'enable-stdio-inheritance': True,
    }).run()


@app.get('/status')
@text_response
def status():
    output = 'Exercise Status:\n'
    for exercise in get_exercises():
        output += f'`-> name:     {exercise.name}\n'
        output += f'    complete: {exercise.complete}\n'
    return output


@app.post('/submit')
@text_response
@reject_handler
def submit():
    # Get options from the form
    user_state = user_state_from_request()
    exercise = run_exercise(user_state)

    return exercise.win_message.format(
        user_exercise_name=user_state.exercise_name,
        user_command=user_state.command,
        user_output=user_state.output,
    )
