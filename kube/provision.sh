#!/bin/sh

# set -e

cd $(dirname $(realpath $0))

echo 'This script will provision your cluster for debugging'

if ! minikube status | grep 'kubelet: Running' &> /dev/null; then
    echo 'staring minikube...' 1>&2
    minikube start --feature-gates=TTLAfterFinished=true
    sleep 1
fi

if ! kubectl config current-context | grep 'minikube' &> /dev/null; then
    echo 'Setting context to minikube' 1>&2
    kubectl config use-context minikube
fi

echo 'Adding traefik ingress label to minikube node...'
kubectl label node minikube traefik=ingress --overwrite

echo 'Adding traefik resources...'
kubectl apply -f ./debug-config/traefik.yml


echo 'Adding nfs'
kubectl create namespace nfs-provisioner
helm install nfs-provisioner ./config/nfs-provisioner --namespace nfs-provisioner


helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

echo 'Adding mariadb'
kubectl create namespace mariadb
helm install mariadb \
     --set 'auth.rootPassword=anubis' \
     --set 'volumePermissions.enabled=true' --set 'auth.username=anubis' \
     --set 'auth.database=anubis' \
     --set 'auth.password=anubis' \
     --set 'replication.enabled=false' \
     --namespace mariadb \
     bitnami/mariadb

