#!/bin/sh

kubectl config use-context minikube
kubectl logs -l app=anubis-api -c api-dev -n anubis
kubectl port-forward svc/anubis-jupyter 5003:5003 -n anubis
