#!/bin/bash

# Change into the directory that this script is in
cd $(dirname $0)
cd ..

# Stop if any commands have an error
set -e

# Be super sure that we aren't accidentially interacting with prod
kubectl config use-context minikube

# Import the minikube docker environment.
# For the rest of this script, when we run docker its connecting
# to the minikube node's docker daemon.
eval $(minikube docker-env)

pushd ..
# Build services in parallel to speed things up
docker-compose build --parallel --pull api web theia-proxy theia-init theia-sidecar
popd

./debug/upgrade.sh

cd ..
make restart
make startup-links
