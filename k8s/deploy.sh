#!/bin/bash

set -e
cd $(dirname $(realpath $0))


pushd ..
#if ! docker image ls | awk '{print $1}' | grep -w '^registry.digitalocean.com/anubis/theia-admin$' &>/dev/null; then
#    EXTRA_BUILD="theia-admin"
#fi
#if ! docker image ls | awk '{print $1}' | grep -w '^registry.digitalocean.com/anubis/theia-xv6$' &>/dev/null; then
#    EXTRA_BUILD="${EXTRA_BUILD} theia-xv6"
#fi
docker-compose build --parallel --pull api web logstash theia-proxy theia-init theia-sidecar ${EXTRA_BUILD}
docker-compose push api web logstash theia-proxy theia-init theia-sidecar ${EXTRA_BUILD}
popd

if ! helm list -n anubis | awk '{print $1}' | grep anubis &> /dev/null; then
    exec helm install anubis ./chart -n anubis $@
else
    exec helm upgrade anubis ./chart -n anubis $@
fi
