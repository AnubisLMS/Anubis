
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
    export PS1="(\[\033[01;34m\]$(current_excercise)\[\033[00m\]) ${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
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