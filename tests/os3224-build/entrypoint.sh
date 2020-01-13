#!/bin/bash

# docker run -it os3224-assignment-n <repo url> <netid> <assignment name> <submission_id>

# This is the entrypoint for the test images. It expects that there are test scripts
# in the working directory (/tmp/build)

# The entrypoint for the assignment test images should not be changed.
# The assignment images should just add their test scripts to the image.

set -e

if (( $# < 3 )); then
    echo "xv6 repo is required" 1>&2
    echo "docker run -it os3224-build <git repo url>" 1>&2
    exit 1
fi


REPO_URL="${1}"
NETID="${2}"
ASSIGNMENT="${3}"


exit_with_failure() {
    # exit_with_failure <msg>

    echo
    echo 'Failed to build xv6.img'
    echo

    echo "${@}" > /mnt/submission/FAIL

    exit 0
}


build() {
    # build the xv6.img file and move it to a more convientent place

    cd /mnt/submission/xv6-public

    # build
    make xv6.img

    if (( $! != 0 )); then
        exit_with_failure 'Failed to build xv6.img'
    fi

    # move
    cd ../
    mv ./xv6-public/xv6.img ../

    # clean
    rm -rf xv6-public
}



main() {
    # Build that image
    build

    # report success
    echo
    echo 'Successfully built xv6.img!'
    echo
}

main
