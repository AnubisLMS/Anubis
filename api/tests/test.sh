#!/usr/bin/env bash

set -e

cd $(dirname $0)

export DEBUG=1
export TEST_ROOT="$(pwd)"
export API_ROOT="$(pwd)/.."
export SOURCE_DIRS="${API_ROOT}/anubis,${API_ROOT}/jobs"

pushd ..
make venv
source venv/bin/activate
popd



export PYTHONPATH="${TEST_ROOT}:${API_ROOT}" DISABLE_ELK=1 DB_HOST=127.0.0.1 REDIS_HOST=127.0.0.1
if (( $# == 0 )); then
    echo 'seeding data...'
    python seed.py 1>/dev/null
fi

if (( COVERAGE == 1 )); then
    echo 'Running tests with coverage...'
    coverage run --source=${SOURCE_DIRS} -m pytest -p no:warnings $@
    mv ${TEST_ROOT}/.coverage ${API_ROOT}
else
    echo 'Running tests...'
    exec pytest -p no:warnings $@
fi
