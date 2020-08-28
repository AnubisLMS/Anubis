#!/bin/sh

set -e

cd $(dirname $(realpath $0))

docker build -t registry.osiris.services/anubis/assignment-base:ubuntu-16.04 .
docker build -t registry.osiris.services/anubis/assignment/1:latest sample_assignment

