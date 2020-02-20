#!/bin/bash

set -e

run_tests() {
    # run all the tests here
    # all the tests should generate report jsons
    for testscript in $(find -name 'test-*.py' | sort); do
        timeout 30 python3 ${testscript} # 2> /dev/null # dont even let students see stdout
    done
}

run_tests
