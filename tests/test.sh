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

echo 'test uploading student data'
anubis -d student ./students.json | jq

echo 'test retreving data'
anubis -d student | jq

echo 'adding assignment'
anubis -d assignment add os3224-assignment-1 '2020-03-07 23:55:00' '2020-03-08 23:55:00' | jq
anubis -d assignment add os3224-assignment-2 '2020-03-07 23:55:00' '2020-03-08 23:55:00' | jq

echo 'test assignment 2'

./assignment2.sh | jq

echo 'giving assignment a hot second to process'
sleep 5

anubis -d stats | jq
anubis -d stats os3224-assignment-2 | jq
anubis -d stats os3224-assignment-2 jmc1283 | jq
