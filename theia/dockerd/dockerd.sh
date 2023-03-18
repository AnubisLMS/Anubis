#!/bin/sh -ex

if [ "${ANUBIS_RUN_DOCKERD}" = "1" ]; then
    echo 'Starting dockerd'
    /usr/local/bin/dockerd-entrypoint.sh --authorization-plugin=anubis-authz
else
    echo 'Skipping dockerd'
    while true; do
        sleep 3600;
    done
fi
