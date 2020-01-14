#!/bin/bash

run_tests() {
    # run all the tests here
    # all the tests should generate report jsons
    for testscript in $(ls test-*.py); do
        python3 ${testscript}
    done
}

ls
pwd
run_tests
