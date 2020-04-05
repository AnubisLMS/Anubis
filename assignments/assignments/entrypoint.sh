#!/bin/bash

#set -e

export REPO_URL="$1"
export NETID="$2"
export ASSIGNMENT_NAME="$3"
export SUBMISSION_ID="$4"

run_tests() {
    # run all the tests here
    # all the tests should generate report jsons
    for testscript in $(find -name 'test-*.py' | sort); do
        timeout 30 python3 ${testscript} 2> /dev/null # dont even let students see stdout
    done
}

run_tests
