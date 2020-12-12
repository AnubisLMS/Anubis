#!/bin/sh

set -e

cd $(dirname $(realpath $0))

anubis assignment build
docker run -it \
       -e DEBUG=1 \
       registry.osiris.services/anubis/assignment/{unique_code} $@

