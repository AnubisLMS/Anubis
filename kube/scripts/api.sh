#!/bin/sh

kubectl config use-context minikube
kubectl port-forward svc/anubis 5000:5000 -n anubis
