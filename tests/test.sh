#!/bin/bash

set -ex

#
# Test the anubis cluster
#

cd $(basename $(realpath $0))

echo 'bringing up services...'
cd ..
make clean debug &> /dev/null
cd tests

echo 'test uploading student data'
anubis -d student ./students.json

echo 'test retreving data'
anubis -d student | jq

echo 'test assignment 2'
curl \
    'https://localhost/public/webhook' \
    -XPOST -ik \
    -H 'content-type: application/json' \
    -H 'X-GitHub-Event: push' \
    --data "$(cat ./webhook2.json)"
