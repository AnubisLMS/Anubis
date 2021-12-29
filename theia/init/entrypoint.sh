#!/bin/bash

set -e

echo "this is changing"

fix_permissions() {
    # Fix permissions
    echo "fixing permissions"
    chown -R 1001:1001 /out
}

# Add motd to bashrc if it is not there already
if ! grep '/etc/motd' /out/.bashrc; then
    echo "adding motd to bashrc"
    echo "" >> /out/.bashrc
    echo "alias python=python3" >> /out/.bashrc
    echo "cat /etc/motd" >> /out/.bashrc
else
    echo "skipping adding motd to bashrc"
fi

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


set +e

# Clone
set -x
cd /out
git clone ${GIT_REPO}
set +x

# Pull any and all repos
for i in $(find . -maxdepth 2 -name '.git' -type d); do
    pushd $(dirname $i)
    git pull --no-verify
    popd
done

fix_permissions
