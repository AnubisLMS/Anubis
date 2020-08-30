#!/bin/sh

set -e

cd $(dirname $(realpath $0))

docker build -t registry.osiris.services/anubis/assignment-base:ubuntu-20.04 .
docker build -t registry.osiris.services/anubis/assignment/1:latest sample_assignment


if [ "$1" = "--push" ]; then
    docker push registry.osiris.services/anubis/assignment-base:ubuntu-20.04
    docker push registry.osiris.services/anubis/assignment/1
fi
