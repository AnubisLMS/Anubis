#!/bin/bash

set -e

#
# Test the anubis cluster
#

cd $(dirname $(realpath $0))

cd ..
if ! docker-compose ps api | grep Up &> /dev/null; then
    echo 'cleaning...'
    make clean &> /dev/null
fi
cd tests

if [ "$1" != "--skip" ]; then
    echo 'bringing up services... (this will take a while)'
    cd ..
    set -x
    docker-compose pull --parallel &> /dev/null &
    make debug  &> /dev/null
    make cli &> /dev/null
    set +x
    cd tests
    echo 'giving anubis a hot second to start...'
    sleep 5
fi

echo 'initializing'
./init.sh

echo 'test assignment 2'
./assignment2.sh | jq

echo 'test assignment 3'
./assignment3.sh | jq

echo 'giving assignment a hot second to process'
sleep 5

anubis -d assignment ls | jq

anubis -d stats os3224-assignment-2 | jq
anubis -d stats os3224-assignment-2 jmc1283 | jq

anubis -d stats os3224-assignment-3 | jq
anubis -d stats os3224-assignment-3 jmc1283 | jq
