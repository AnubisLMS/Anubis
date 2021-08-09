#!/bin/bash

set -e

if [ ! "${GIT_REPO}" ]; then
    echo "GIT_REPO is empty, exiting"
    exit 0
fi

if [ -n "${GIT_CRED}" ]; then
    echo "${GIT_CRED}" > /root/.git-credentials
    echo "[credential]" >> /root/.gitconfig
    echo "    helper = store" >> /root/.gitconfig
fi

set -x

# Clone
cd /out
git clone ${GIT_REPO}

set +x

# Pull any and all repos
for i in $(find . -maxdepth 2 -name '.git' -type d); do
    pushd $(dirname $i)
    git pull --no-verify
    popd
done

# Fix permissions
chown -R 1001:1001 /out
