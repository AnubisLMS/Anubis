#!/bin/bash

set -e
cd $(dirname $(realpath $0))


kubectl config use-context space


if ! kubectl get namespace | grep anubis &> /dev/null; then
    kubectl create namespace anubis
fi


if ! kubectl get secrets -n anubis | grep api &> /dev/null; then
    read -s -p "Anubis DB Password: " DB_PASS
    read -s -p "Anubis REDIS Password: " REDIS_PASS
    kubectl create secret generic api \
            --from-literal=database-uri=mysql+pymysql://anubis:${DB_PASS}@mariadb.mariadb.svc.cluster.local/anubis \
            --from-literal=database-password=${DB_PASS} \
            --from-literal=redis-password=${REDIS_PASS} \
            --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
            -n anubis
fi


if ! helm list -n anubis | awk '{print $1}' | grep elasticsearch &> /dev/null; then
    # Install a minimal elasticsearch and kibana deployments
    echo 'Adding elasticsearch + kibana'
    helm  upgrade --install elasticsearch bitnami/elasticsearch \
        --set name=elasticsearch \
        --set master.persistence.size=4Gi \
        --set data.persistence.size=4Gi \
        --set master.replicas=2 \
        --set coordinating.replicas=2 \
        --set data.replicas=2 \
        --set global.kibanaEnabled=true \
        --set fullnameOverride=elasticsearch \
        --set global.coordinating.name=coordinating \
        --namespace anubis

    read -s -p "Anubis REDIS Password: " REDIS_PASS
    # Install a minimal redis deployment
    echo 'Adding redis'
    helm upgrade --install redis bitnami/redis \
        --set fullnameOverride=redis \
        --set global.redis.password=${REDIS_PASS} \
        --set architecture=standalone \
        --set master.persistence.enabled=false \
        --namespace anubis
fi


pushd ..
if ! docker image ls | awk '{print $1}' | grep -w '^registry.osiris.services/anubis/theia-admin$' &>/dev/null; then
    EXTRA_BUILD="theia-admin"
fi
if ! docker image ls | awk '{print $1}' | grep -w '^registry.osiris.services/anubis/theia-xv6$' &>/dev/null; then
    EXTRA_BUILD="${EXTRA_BUILD} theia-xv6"
fi
docker-compose build --parallel --pull api web logstash theia-proxy theia-init theia-sidecar ${EXTRA_BUILD}
docker-compose push api web logstash theia-admin theia-xv6 theia-proxy theia-init theia-sidecar
popd

if ! helm list -n anubis | awk '{print $1}' | grep anubis &> /dev/null; then
    exec helm install anubis ./chart -n anubis $@
else
    exec helm upgrade anubis ./chart -n anubis $@
fi
