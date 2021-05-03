#!/bin/sh

set -e

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"
cd ${1:-/home/project}

echo "Autosaving @ $(date)"

git push --no-verify
git add .
git commit --no-verify -m "Anubis Cloud IDE Autosave"
git push --no-verify
