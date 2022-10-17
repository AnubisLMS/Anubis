#!/usr/bin/python3

import dataclasses
import functools
import logging
import os
import re

from flask import Flask, Response, request, make_response

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

NETID = os.environ.get('NETID', default=None)
ADMIN = os.environ.get('ANUBIS_ADMIN', default=None) == 'ON'
TOKEN = os.environ.get('TOKEN', default=None)
GIT_REPO = os.environ.get('GIT_REPO', default='')
GIT_REPO_PATH = '/home/anubis/' + GIT_REPO.split('/')[-1]

logging.info(f'TOKEN = {TOKEN}')
logging.info(f'GIT_REPO = {GIT_REPO}')
logging.info(f'GIT_REPO_PATH = {GIT_REPO_PATH}')


def text_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        r = func(*args, **kwargs)

        if not isinstance(r, tuple):
            message: str = r
            status_code: int = 200
        else:
            message, status_code = r

        r = make_response(message + '\n')
        r.status_code = status_code
        r.headers['Content-Type'] = 'text/plain'
        return r

    return wrapper


@dataclasses.dataclass
class Exercise:
    name: str = None
    win_message: str = 'Congrats! You did the exercise by typing {user_command}'
    command_regex: re.Pattern = None
    output_regex: re.Pattern = None
    complete: bool = False


exercises = {
    'helloworld': Exercise(
        name='helloworld',
        command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"?'),
        output_regex=re.compile(r'[Hh]ello\s[Ww]orld!?'),
    ),
}


@app.get('/status')
@text_response
def status():
    output = 'Exercise Status:\n'
    for exercise in exercises.values():
        output += f'`-> name:     {exercise.name}\n'
        output += f'    complete: {exercise.complete}\n'
    return output


@app.post('/submit')
@text_response
def submit():
    # Get options from the form
    user_exercise_name: str = request.form.get('exercise', default='').strip()
    user_command: str = request.form.get('command', default='')
    user_output: str = request.form.get('output', default='')

    # Log
    app.logger.info(f'user_exercise_name = {user_exercise_name}')
    app.logger.info(f'user_command = {user_command}')
    app.logger.info(f'user_output = {user_output}')

    exercise = exercises.get(user_exercise_name, None)
    if exercise is None:
        return 'Exercise not found!', 406

    # Check command against regex
    if exercise.command_regex is not None:
        command_match = exercise.command_regex.match(user_command)
        if command_match is None:
            return 'Sorry your command does not seem right.'

    # Check output against regex
    if exercise.output_regex is not None:
        output_match = exercise.output_regex.match(user_output)
        if output_match is None:
            return 'Sorry your output does not seem right.'

    # Mark exercise as complete
    exercise.complete = True

    return exercise.win_message.format(
        user_exercise_name=user_exercise_name,
        user_command=user_command,
        user_output=user_output,
    )
