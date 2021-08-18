#!/bin/bash

set -e

fix_permissions() {
    # Fix permissions
    echo "fixing permissions"
    chown -R 1001:1001 /out
}

# Copy things like .bashrc and .profile from /etc/skel if
# they dont exist in the volume.
for i in $(ls -A /etc/skel/); do
    if [ ! -f /out/$i ]; then
        cp /etc/skel/$i /out/$i
    fi
done

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