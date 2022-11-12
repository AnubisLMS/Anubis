#!/usr/bin/python3

"""
#!/bin/bash

EXERCISES=(
    "helloworld"
    "mkdir exercise1"
    "cd exercise1"
    "pipe hello world"
)
EXERCISE_INDEX=0

status() {
    curl http://localhost:5003/status -s
}

current_excercise() {
    echo ${EXERCISES[EXERCISE_INDEX]}
}

set_ps1() {
    export PS1="($(current_excercise)) ${debian_chroot:+($debian_chroot)}\u@\h:\w\$ "
}

check_exercise() {
    EXERCISE=$(current_excercise)
    COMMAND=$(HISTTIMEFORMAT= history 1 | sed -e "s/^[ ]*[0-9]*[ ]*//")
    OUTPUT=$(cat /tmp/output 2>&1)
    [ "$COMMAND" = "status" ] && return
    STATUS_CODE=$(curl http://localhost:5003/submit \
        --output /dev/stderr --write-out "%{http_code}" \
        --data "exercise=${EXERCISE}" \
        --data "command=${COMMAND}" \
        --data "output=${OUTPUT}" \
        --data "cwd=${PWD}" \
        -s)
    if (( $STATUS_CODE == 200 )); then
        EXERCISE_INDEX=$(( $EXERCISE_INDEX + 1 ))
    fi
    set_ps1
}
PROMPT_COMMAND="check_exercise"

preexec_invoke_exec () {
    [ -n "$COMP_LINE" ] && return
    [ "$BASH_COMMAND" = "$PROMPT_COMMAND" ] && return
    [ "$BASH_COMMAND" = "status" ] && return

    exec 1>&3
    rm -f /tmp/output /tmp/command
    echo "$BASH_COMMAND" > /tmp/command
    exec > >(tee /tmp/output)
}

rm -f /tmp/output
exec 3>&1
trap 'preexec_invoke_exec' DEBUG

set_ps1
"""

import logging
import os

from flask import Flask

from autograde.exercise import run_exercise, exercises
from autograde.utils import text_response, reject_handler, user_state_from_request

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


@app.get('/status')
@text_response
def status():
    output = 'Exercise Status:\n'
    for exercise in exercises.values():
        output += f'`-> name:     {exercise.name}\n'
        output += f'    requires: {exercise.requires_exercises}\n'
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
