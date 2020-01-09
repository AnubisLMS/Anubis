#!/bin/bash

if (( $# < 1 )); then
    echo "xv6 repo is required" 1>&2
    echo "docker run -it os3224-build <git repo url>" 1>&2
    exit 1
fi

# clone the repo
REPO_URL="${1}"
git clone ${REPO_URL} xv6-public
cd xv6-public

# build the image
make xv6.img

# run tests
# ./test.sh
echo 'built xv6.img'
