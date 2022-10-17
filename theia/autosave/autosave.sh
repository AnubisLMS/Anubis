#!/bin/bash

set -e

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"
cd ${1:-/home/anubis}

echo "Autosaving @ $(date)"

# Commit and push any and all repos
for i in $(find . -maxdepth 2 -name '.git' -type d); do
    pushd $(dirname $i)
    git -c 'core.hooksPath=/dev/null' -c 'alias.push=push' push --no-verify "${GIT_REPO}"
    git -c 'core.hooksPath=/dev/null' -c 'alias.add=add' add .
    git -c 'core.hooksPath=/dev/null' -c 'alias.commit=commit' commit --no-verify -m "Anubis Cloud IDE Autosave netid=${NETID}"
    git -c 'core.hooksPath=/dev/null' -c 'alias.push=push' push --no-verify "${GIT_REPO}"
    popd
done

