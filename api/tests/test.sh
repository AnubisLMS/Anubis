#!/usr/bin/env bash

set -e

cd $(dirname $0)

TEST_ROOT="$(pwd)"
API_ROOT="$(pwd)/.."

pushd ..
make venv
source venv/bin/activate
popd


export PYTHONPATH="${TEST_ROOT}:${API_ROOT}"
exec pytest -p no:warnings $@
