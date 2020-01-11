#!/bin/bash

# docker run -it os3224-assignment-n <repo url> <netid> <assignment name>

# This is the entrypoint for the test images. It expects that there are test scripts
# in the working directory (/tmp/build)

# The entrypoint for the assignment test images should not be changed.
# The assignment images should just add their test scripts to the image.

if (( $# < 3 )); then
    echo "xv6 repo is required" 1>&2
    echo "docker run -it os3224-build <git repo url>" 1>&2
    exit 1
fi


REPO_URL="${1}"
NETID="${2}"
ASSIGNMENT="${3}"

build() {
    # clone the repo then build the xv6.img file and move it to a more convientent place

    # clone
    git clone ${REPO_URL} xv6-public
    cd xv6-public

    # build
    make xv6.img

    # move
    cd ../
    mv ./xv6-public/xv6.img ./

    # clean
    rm -rf xv6-public

    echo 'built xv6.img'
}


run_test() {
    # run each of the test scripts (all scripts matching test-*.sh)
    for test_script in $(ls test-*.py | sort); do
        python3 ${test_script}
    done
}


report_results() {
    # Report results to api
    python3 report.py ${NETID} ${ASSIGNMENT}
}


main() {
    # Build that image
    build

    # Run those tests
    run_tests

    # Report those results
    report_results
}

main
