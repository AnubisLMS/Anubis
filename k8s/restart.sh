#!/bin/sh

set -e

kubectl rollout restart deploy -n anubis \
        anubis-api \
        anubis-web \
        anubis-pipeline-api \
        anubis-theia-proxy \
        anubis-rpc-default \
        anubis-rpc-theia \
        anubis-rpc-regrade
