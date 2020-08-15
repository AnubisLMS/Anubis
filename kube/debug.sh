#!/bin/bash

cd $(dirname $(realpath $0))


kubectl config use-context minikube
eval $(minikube -p minikube docker-env)

if ! kubectl get namespace | grep anubis &> /dev/null; then
    kubectl create namespace anubis
fi

if ! kubectl get secrets -n anubis | grep api &> /dev/null; then
    kubectl create secret generic api \
            --from-literal=database-uri=mysql+pymysql://anubis:anubis@mariadb.mariadb.svc.cluster.local/anubis \
            -n anubis
fi



pushd ..
docker-compose build --parallel
# docker-compose push
popd

kubectl apply \
        -f config/api.yml \
        -f config/web-static.yml \
        -f config/elk.yml \
        -f config/redis.yml

