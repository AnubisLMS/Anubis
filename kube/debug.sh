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
            --from-literal=database-password=anubis \
            --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
            -n anubis

    kubectl create secret generic oauth \
            --from-literal=consumer-key='aaa' \
            --from-literal=consumer-secret='aaa' \
            -n anubis
fi



pushd ..
docker-compose build api
docker-compose build --parallel web logstash static theia-proxy theia-init
if ! docker image ls | awk '{print $1}' | grep 'registry.osiris.services/anubis/api-dev' &>/dev/null; then
    docker-compose build api-dev
fi
if ! docker image ls | awk '{print $1}' | grep -w '^registry.osiris.services/anubis/theia$' &>/dev/null; then
    docker-compose build theia
fi
popd

../pipeline/build.sh

if helm list -n anubis | grep anubis &> /dev/null; then
    helm upgrade anubis . -n anubis \
         --set "imagePullPolicy=IfNotPresent" \
         --set "elasticsearch.storageClassName=standard" \
         --set "debug=true" \
         --set "api.replicas=1" \
         --set "static.replicas=1" \
         --set "web.replicas=1" \
         --set "pipeline_api.replicas=1" \
         --set "rpc_workers.replicas=1" \
         --set "theia.proxy.replicas=1" \
         --set "theia.proxy.domain=ide.localhost" \
         --set "rollingUpdates=false" \
         --set "domain=localhost" \
         --set "elasticsearch.initContainer=false" $@
else
    helm install anubis . -n anubis \
         --set "imagePullPolicy=IfNotPresent" \
         --set "elasticsearch.storageClassName=standard" \
         --set "debug=true" \
         --set "api.replicas=1" \
         --set "static.replicas=1" \
         --set "web.replicas=1" \
         --set "pipeline_api.replicas=1" \
         --set "rpc_workers.replicas=1" \
         --set "theia.proxy.replicas=1" \
         --set "theia.proxy.domain=ide.localhost" \
         --set "rollingUpdates=false" \
         --set "domain=localhost" \
         --set "elasticsearch.initContainer=false" $@
fi

kubectl rollout restart deployments.apps/api -n anubis
kubectl rollout restart deployments.apps/pipeline-api -n anubis
kubectl rollout restart deployments.apps/rpc-workers  -n anubis
kubectl rollout restart deployments.apps/theia-proxy  -n anubis
