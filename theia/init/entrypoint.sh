#!/bin/bash

set -e

echo "this is changing"

fix_permissions() {
    # Fix permissions
    echo "fixing permissions"
    chown -R 1001:1001 /home/anubis
}

init_home() {
    # make .anubis
    mkdir -p /home/anubis/.anubis
}

init_home
fix_permissions

if [ ! "${GIT_REPO}" ]; then
    echo "GIT_REPO is empty, exiting"
    exit 0
fi

if [ -n "${GIT_CRED}" ]; then
    echo "${GIT_CRED}" > /root/.git-credentials
    echo "[credential]" >> /root/.gitconfig
    echo "    helper = store" >> /root/.gitconfig
fi

git config --global core.hooksPath /dev/null

set +e

# Clone
set -x
cd /home/anubis
git clone ${GIT_REPO}
set +x

fix_permissions
