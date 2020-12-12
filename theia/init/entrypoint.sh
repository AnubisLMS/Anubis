#!/bin/sh

set -e

if [ -n "${GIT_CRED}" ]; then
    echo "${GIT_CRED}" > /root/.git-credentials
    echo "[credential]" >> /root/.gitconfig
    echo "    helper = store" >> /root/.gitconfig
fi

set -x

# Clone
git clone ${GIT_REPO} /out

# Fix permissions
chown -R 1001:1001 /out
