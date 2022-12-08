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
     --set "rpc.replicas=1" \
     --set "theia.proxy.replicas=1" \
     --set "api.datacenter=false" \
     --set "theia.proxy.domain=ide.localhost" \
     --set "rollingUpdates=false" \
     --set "domain=localhost" \
     --set "discord_bot.replicas=0" \
     --set "reaper.suspend=true" \
     --set "visuals.suspend=true" \
     --set "backup.suspend=true" \
     --set "autograde_recalculate.suspend=true" \
     --set "daily_cleanup.suspend=true" \
     --set "theia.prop.enable=false" \
     --set "marketing.enable=false" \
     --set "tag=latest" \
     $@
