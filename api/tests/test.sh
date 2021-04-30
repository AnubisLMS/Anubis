#!/usr/bin/env bash

set -e

cd $(dirname $0)

TEST_ROOT="$(pwd)"
API_ROOT="$(pwd)/.."

pushd ..
make venv
source venv/bin/activate
popd



export PYTHONPATH="${TEST_ROOT}:${API_ROOT}" DISABLE_ELK=1 DB_HOST=127.0.0.1
if (( $# == 0 )); then
    echo 'seeding data...'
    python seed.py &>/dev/null
fi

echo 'Running tests...'
exec pytest -p no:warnings $@
