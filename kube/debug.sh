#!/bin/bash

# Change into the directory that this script is in
cd $(dirname $0)

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

# Build demo assignment pipeline image
pushd ../demo
./build.sh
popd

pushd ..
# Build services in parallel to speed things up
docker-compose build --parallel --pull api web logstash theia-proxy theia-init theia-sidecar
popd

# Figure out if we are upgrading or installing
if helm list -n anubis | awk '{print $1}' | grep anubis &> /dev/null; then
    HELM_COMMAND=upgrade
else
    HELM_COMMAND=install
fi

# Upgrade or install minimal anubis cluster in debug mode
helm ${HELM_COMMAND} anubis . -n anubis \
     --set "imagePullPolicy=IfNotPresent" \
     --set "elasticsearch.storageClassName=standard" \
     --set "debug=true" \
     --set "api.replicas=1" \
     --set "web.replicas=1" \
     --set "pipeline_api.replicas=1" \
     --set "rpc.default.replicas=1" \
     --set "rpc.theia.replicas=1" \
     --set "theia.proxy.replicas=1" \
     --set "api.datacenter=false" \
     --set "theia.proxy.domain=ide.localhost" \
     --set "rollingUpdates=false" \
     --set "domain=localhost" \
     $@

# Restart the most common deployments
kubectl rollout restart deployments.apps/api -n anubis
kubectl rollout restart deployments.apps/web -n anubis
kubectl rollout restart deployments.apps/pipeline-api -n anubis
kubectl rollout restart deployments.apps/rpc-default  -n anubis
kubectl rollout restart deployments.apps/rpc-theia  -n anubis
kubectl rollout restart deployments.apps/theia-proxy  -n anubis


echo
echo 'seed: https://localhost/api/admin/seed/'
echo 'auth: https://localhost/api/admin/auth/token/jmc1283'
echo 'site: https://localhost/'

# Only build theia if it doesnt already exist (it's a long build)
if ! docker image ls | awk '{print $1}' | grep -w '^registry.osiris.services/anubis/theia-admin$' &>/dev/null; then
    docker-compose build --parallel theia-admin theia-xv6
fi
