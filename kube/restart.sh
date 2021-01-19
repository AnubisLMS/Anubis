#!/bin/sh

set -e

kubectl rollout restart deployments.apps/api -n anubis
kubectl rollout restart deployments.apps/web -n anubis
kubectl rollout restart deployments.apps/pipeline-api -n anubis
kubectl rollout restart deployments.apps/rpc-workers  -n anubis
kubectl rollout restart deployments.apps/theia-proxy  -n anubis
