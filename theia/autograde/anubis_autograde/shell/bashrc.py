import argparse
import os

import jinja2

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.logging import log

bashrc_template = jinja2.Template("""
#!/bin/bash

GRADE_URL=http://localhost:5003
EXERCISES=(
{% for exercise in exercises %}
    "{{ exercise.name }}"
{% endfor %}
)
EXERCISE_INDEX=$(curl ${GRADE_URL}/current -s || echo 0)

curl ${GRADE_URL}/start -s

reset() {
    EXERCISE_INDEX=$(curl ${GRADE_URL}/reset -s)
    set_ps1
}

status() {
    curl ${GRADE_URL}/status -s
}

hint() {
    curl ${GRADE_URL}/hint -s
}

current_exercise() {
    echo ${EXERCISES[EXERCISE_INDEX]}
}

set_ps1() {
    export PS1="(\\[\\033[01;34m\\]$(current_exercise)\\[\\033[00m\\]) ${debian_chroot:+($debian_chroot)}\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ "
}

check_exercise() {
    EXERCISE=$(current_exercise)
    ENVIRONMENT=$(env | base64 --ignore-garbage)
    COMMAND=$(cat /tmp/command 2>&1)
    OUTPUT=$(cat /tmp/output 2>&1)
    [ "$COMMAND" = "status" ] && return
    [ "$COMMAND" = "hint" ] && return
    [ "$COMMAND" = "reset" ] && return
    [ "$COMMAND" = "set_ps1" ] && return
    [ "$COMMAND" = "" ] && return
    STATUS_CODE=$(curl ${GRADE_URL}/submit \\
        --output /dev/stderr --write-out "%{http_code}" \\
        --data "exercise=${EXERCISE}" \\
        --data "command=${COMMAND}" \\
        --data "output=${OUTPUT}" \\
        --data "cwd=${PWD}" \\
        --data "env=${ENVIRONMENT}" \\
        -s)
    if (( $STATUS_CODE == 200 )); then
        EXERCISE_INDEX=$(( $EXERCISE_INDEX + 1 ))
    fi
    echo -n > /tmp/output > /tmp/command
    set_ps1
}
PROMPT_COMMAND="check_exercise"

preexec_invoke_exec () {
    [ "$BASH_COMMAND" = "$PROMPT_COMMAND" ] && return
    [ "$BASH_COMMAND" = "status" ] && return
    [ "$BASH_COMMAND" = "hint" ] && return
    [ "$BASH_COMMAND" = "reset" ] && return

    exec 1>&3
    rm -f /tmp/output /tmp/command
    echo "$BASH_COMMAND" > /tmp/command
    exec > >(tee /tmp/output)
}

rm -f /tmp/output
exec 3>&1
trap 'preexec_invoke_exec' DEBUG

set_ps1
""")


def init_bashrc(args: argparse.Namespace):
    exercises = get_exercises()

    home = os.environ['HOME']
    bashrc_dir = home if args.prod else os.getcwd()
    bashrc_path = os.path.join(bashrc_dir, '.bashrc')

    log.info(f'Generating shell rc {bashrc_path=} {exercises=}')

    bashrc = bashrc_template.render(exercises=exercises)
    log.debug(bashrc)
    with open(bashrc_path, 'w') as bashrc_file:
        bashrc_file.write(bashrc)
