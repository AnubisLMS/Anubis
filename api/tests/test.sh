#!/usr/bin/env bash

cd $(dirname $(realpath $0))

API_ROOT="$(realpath ..)"

for test_file in $(find -name '*test.py'); do
    echo "${test_file}"
    env PYTHONPATH=${API_ROOT}:${PYTHONPATH} python3 ${test_file}
done
