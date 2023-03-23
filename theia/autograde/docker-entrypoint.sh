#!/usr/bin/env bash

if [ "${EXERCISE_PY}" != "" ]; then
    echo "${EXERCISE_PY}" | tee /opt/anubis/exercise.py
fi

unset exercise.py

exec supervisord --nodaemon -c /supervisord.conf