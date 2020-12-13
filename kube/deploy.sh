#!/bin/bash

set -e
cd $(dirname $(realpath $0))


kubectl config use-context space


if ! kubectl get namespace | grep anubis &> /dev/null; then
    kubectl create namespace anubis
fi


if ! kubectl get secrets -n anubis | grep api &> /dev/null; then
    read -s -p "Anubis DB Password: " DB_PASS
    kubectl create secret generic api \
            --from-literal=database-uri=mysql+pymysql://anubis:${DB_PASS}@mariadb.mariadb.svc.cluster.local/anubis \
            --from-literal=database-password=${DB_PASS} \
            --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
            -n anubis
fi


pushd ..
docker-compose build --parallel api web logstash static theia-proxy theia-init theia-sidecar
if ! docker image ls | awk '{print $1}' | grep 'registry.osiris.services/anubis/api-dev' &>/dev/null; then
   docker-compose build api-dev
fi
if ! docker image ls | awk '{print $1}' | grep -w '^registry.osiris.services/anubis/theia$' &>/dev/null; then
    docker-compose build theia
fi
docker-compose push api web logstash static theia-proxy theia-init theia-sidecar
popd


helm upgrade anubis . -n anubis $@

# kubectl apply \
#         -f config/api.yml \
#         -f config/web-static.yml \
#         -f config/elk.yml \
#         -f config/redis.yml \
#         -f config/pipeline-api.yml \
#         -f config/rpc-workers.yml


# kubectl rollout restart deployments.apps/api -n anubis
# kubectl rollout restart deployments.apps/web -n anubis
# kubectl rollout restart deployments.apps/pipeline-api -n anubis
# kubectl rollout restart deployments.apps/rpc-workers  -n anubis
