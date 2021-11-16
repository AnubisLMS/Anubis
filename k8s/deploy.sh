#!/bin/bash

set -e
cd $(dirname $(realpath $0))

BUILD=(
    api
    web
    old-web
    theia-proxy
    theia-init
    theia-sidecar
)

pushd ..
docker-compose build --parallel --pull ${BUILD[@]} ${EXTRA_BUILD}
docker-compose push ${BUILD[@]} ${EXTRA_BUILD}
popd

exec helm upgrade --install anubis ./chart -n anubis $@
