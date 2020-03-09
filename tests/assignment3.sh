#!/bin/bash


cd $(dirname $(realpath $0))

curl \
    'https://api.localhost/public/webhook' \
    -XPOST -k \
    -H 'content-type: application/json' \
    -H 'X-GitHub-Event: push' \
    --data "$(cat ./webhook3.json)"
