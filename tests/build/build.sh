#!/bin/bash

if (( $# < 1 )); then
    echo "xv6 repo is required" 1&>2
    echo "docker run -it <image tag> <git repo url>" 1&>2
    exit 1
fi

REPO_URL="${1}"

git clone ${REPO_URL}

make xv6.img
