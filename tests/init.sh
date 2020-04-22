#!/bin/sh

set -e

#
# initialize studnt and assignment data for tests
#

cd $(dirname $(realpath $0))


echo 'test uploading student data'
anubis -d student ./students.json | jq

echo 'test retreving data'
anubis -d student | jq

echo 'adding assignment'
anubis -d assignment add os3224-assignment-1 '2020-03-07 23:55:00' '2020-03-08 23:55:00' | jq
anubis -d assignment add os3224-assignment-2 '2020-03-07 23:55:00' '2020-03-08 23:55:00' | jq
anubis -d assignment add os3224-assignment-3 '2020-04-05 23:55:00' '2020-04-06 23:55:00' | jq
anubis -d assignment add midterm '2020-04-13 23:55:00' '2020-04-13 23:55:00' | jq
anubis -d assignment add os3224-assignment-4 '2020-05-20 23:55:00' '2020-05-21 23:55:00' | jq
