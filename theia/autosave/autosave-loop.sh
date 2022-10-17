#!/bin/sh

set -e

if [ -n "${GIT_CRED}" ]; then
    echo "${GIT_CRED}" > /home/theia/.git-credentials
    git config --global credential.store helper
    git config --global credential.helper 'store --file ~/.git-credentials'
    git config --global user.email anubis@anubis-lms.io
    git config --global user.name anubis-robot
    git config --global core.hooksPath /dev/null
fi

set +e
while true; do
    if [ "${AUTOSAVE}" = "ON" ] && [ -n "${GIT_CRED}" ]; then
        /autosave.sh
    fi
    sleep "5m"
done
