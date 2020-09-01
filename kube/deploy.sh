#!/bin/bash

cd $(dirname $(realpath $0))


kubectl config use-context space

if ! kubectl get namespace | grep anubis &> /dev/null; then
    kubectl create namespace anubis
fi

if ! kubectl get secrets -n anubis | grep api &> /dev/null; then
    kubectl create secret generic api \
            --from-literal=database-uri=mysql+pymysql://anubis:anubis@mariadb.mariadb.svc.cluster.local/anubis \
            --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
            -n anubis
fi



pushd ..
docker-compose build api
docker-compose build --parallel web logstash
docker-compose push
popd

../pipeline/build.sh --push

docker push registry.osiris.services/anubis/assignment-base:ubuntu-16.04
docker push registry.osiris.services/anubis/assignment/1:latest

kubectl apply \
        -f config/api.yml \
        -f config/web-static.yml \
        -f config/elk.yml \
        -f config/redis.yml \
        -f config/pipeline-api.yml \
        -f config/rpc-workers.yml


kubectl rollout restart deployments.apps/anubis-api -n anubis
kubectl rollout restart deployments.apps/anubis-pipeline-api -n anubis
kubectl rollout restart deployments.apps/anubis-rpc-workers  -n anubis
