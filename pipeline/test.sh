#!/bin/sh

set -e

cd $(dirname $(realpath $0))

./build.sh

docker run -it \
       -e TOKEN=test \
       -e COMMIT=2bc7f8d636365402e2d6cc2556ce814c4fcd1489 \
       -e GIT_REPO=https://github.com/juan-punchman/xv6-public.git \
       -e SUBMISSION_ID=1 \
       registry.osiris.services/anubis/assignment/1 $@

