#!/bin/sh

set -ex

cd $(dirname $(realpath $0))

echo 'This script will provision your cluster for debugging'

if ! kubectl config current-context | grep 'minikube' &> /dev/null; then
    echo 'This script will only work with the minikube context' 2&>1
    echo 'If you have minkube installed: ' 2&>1
    echo 'kubectl config use-context minikube' 2&>1
    exit 1
fi

echo 'Adding traefik ingress label to minikube node...'
kubectl label node minikube traefik=ingress --overwrite

echo 'Adding traefik resources...'
kubectl apply -f traefik.yml


echo 'Adding kubenetes-dashbord resources...'
kubectl apply -f dashboard.yml


echo 'Adding nfs'
kubectl create namespace nfs-provisioner
helm install nfs-provisioner ./nfs-provisioner --namespace nfs-provisioner
