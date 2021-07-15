#!/bin/sh

set -e

if [ -n "${GIT_CRED}" ]; then
    echo "${GIT_CRED}" > /home/theia/.git-credentials
    git config --global credential.store helper
    git config --global credential.helper 'store --file ~/.git-credentials'
    git config --global user.email anubis@osiris.cyber.nyu.edu
    git config --global user.name anubis-robot
fi

set +e
while true; do
    if [ "${AUTOSAVE}" = "ON" ]; then
        /autosave.sh
    fi
    sleep "5m"
done
