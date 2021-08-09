#!/bin/sh

set -e

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"
cd ${1:-/home/anubis}

echo "Autosaving @ $(date)"

# Commit and push any and all repos
for i in $(find . -maxdepth 2 -name '.git' -type d); do
    pushd $(dirname $i)
    git push --no-verify
    git add .
    git commit --no-verify -m "Anubis Cloud IDE Autosave"
    git push --no-verify
    popd
done

