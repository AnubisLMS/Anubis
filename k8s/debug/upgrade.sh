#!/bin/sh

cd $(dirname $(realpath $0))
cd ..

kubectl config use-context minikube

# Upgrade or install minimal anubis cluster in debug mode
helm upgrade \
     --install anubis ./chart \
     --namespace anubis \
     --set "imagePullPolicy=IfNotPresent" \
     --set "elasticsearch.storageClassName=standard" \
     --set "debug=true" \
     --set "api.replicas=1" \
     --set "web.replicas=1" \
     --set "pipeline_api.replicas=1" \
     --set "rpc.default.replicas=1" \
     --set "rpc.theia.replicas=1" \
     --set "rpc.regrade.replicas=1" \
     --set "theia.proxy.replicas=1" \
     --set "api.datacenter=false" \
     --set "reaper.suspend=true" \
     --set "visuals.suspend=true" \
     --set "theia.proxy.domain=ide.localhost" \
     --set "rollingUpdates=false" \
     --set "domain=localhost" \
     $@
