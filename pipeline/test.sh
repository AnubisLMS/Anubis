#!/bin/sh

set -e

docker build -t registry.osiris.services/anubis/assignment-base:ubuntu-16.04 .
docker build -t assignment-1 sample_assignment

docker run -it \
       -e TOKEN=test \
       -e COMMIT=2bc7f8d636365402e2d6cc2556ce814c4fcd1489 \
       -e GIT_REPO=https://github.com/juan-punchman/xv6-public.git \
       -e SUBMISSION_ID=1 \
       assignment-1 $@

