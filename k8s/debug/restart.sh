#!/bin/bash

# Change into the directory that this script is in
cd $(dirname $0)
cd ..

# Stop if any commands have an error
set -e

# Be super sure that we aren't accidentially interacting with prod
kubectl config use-context minikube

# Make sure we have an anubis namespace
if ! kubectl get namespace | grep anubis &> /dev/null; then
    kubectl create namespace anubis
fi

if ! kubectl get secrets -n anubis | grep api &> /dev/null; then
    # Create the api configuration secrets
    kubectl create secret generic api \
            --from-literal=database-uri=mysql+pymysql://anubis:anubis@mariadb.mariadb.svc.cluster.local/anubis \
            --from-literal=database-password=anubis \
            --from-literal=redis-password=anubis \
            --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
            -n anubis

    # Create the oauth configuration secrets
    kubectl create secret generic oauth \
            --from-literal=consumer-key='aaa' \
            --from-literal=consumer-secret='aaa' \
            -n anubis
fi

# Import the minikube docker environment.
# For the rest of this script, when we run docker its connecting
# to the minikube node's docker daemon.
eval $(minikube docker-env)

pushd ..
# Build services in parallel to speed things up
docker-compose build --parallel --pull api web logstash theia-proxy theia-init theia-sidecar
popd

./debug/upgrade.sh

# Restart the most common deployments
kubectl rollout restart deployments.apps/api -n anubis
kubectl rollout restart deployments.apps/web -n anubis
kubectl rollout restart deployments.apps/rpc-default -n anubis
kubectl rollout restart deployments.apps/rpc-theia -n anubis
kubectl rollout restart deployments.apps/rpc-regrade -n anubis
kubectl rollout restart deployments.apps/pipeline-api -n anubis
kubectl rollout restart deployments.apps/theia-proxy -n anubis
