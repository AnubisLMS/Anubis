#!/bin/sh

set -e

cd $(dirname $(realpath $0))

docker build -t registry.osiris.services/anubis/assignment-base:latest .


if [ "$1" = "--push" ]; then
    docker push registry.osiris.services/anubis/assignment-base:latest
fi
