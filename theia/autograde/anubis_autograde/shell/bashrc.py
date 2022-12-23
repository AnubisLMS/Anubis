import argparse
import os

import jinja2

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.logging import log

bashrc_template = jinja2.Template("""
#!/bin/bash

[[ $- == *i* ]] || return

GRADE_URL=http://localhost:5003
EXERCISES=(
{% for exercise in exercises %}
    "{{ exercise.name }}"
{% endfor %}
)
EXERCISE_INDEX=$(curl ${GRADE_URL}/current -s || echo 0)


start_message() {
    curl ${GRADE_URL}/start -s
}

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
    [ "$COMMAND" = '__vsc_original_prompt_command=$PROMPT_COMMAND' ] && return
    [ "$COMMAND" = "start_message" ] && return
    [ "$COMMAND" = "status" ] && return
    [ "$COMMAND" = "hint" ] && return
    [ "$COMMAND" = "reset" ] && return
    [ "$COMMAND" = "set_ps1" ] && return
    [ "$COMMAND" = "" ] && return
    
    if (( $EXERCISE_INDEX == -1 )); then
        return
    fi
    
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

jrun() {
    case "$1" in
        "start_message"|"status"|"hint"|"reset"|"set_ps1"|"return")
            eval "$1"
            return
            ;;
        *)
            echo "$1" > /tmp/command
            eval "$1" > >(tee /tmp/output)
            check_exercise
            ;;
    esac
}

export PATH=${HOME}/bin:${PATH}
rm -f /tmp/output

set_ps1
start_message
""")


def init_bashrc(args: argparse.Namespace):
    exercises = get_exercises()

    home = os.environ['HOME']
    bashrc_dir = home if args.prod else os.getcwd()
    bashrc_path = os.path.join(bashrc_dir, '.bashrc')

    log.info(f'Generating shell rc bashrc_path={bashrc_path} exercises={exercises}')

    bashrc = bashrc_template.render(exercises=exercises)
    log.debug(bashrc)
    with open(bashrc_path, 'w') as bashrc_file:
        bashrc_file.write(bashrc)
