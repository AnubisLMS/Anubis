#!/bin/sh

kubectl logs -l app=anubis-debug -c jupyter -n anubis
kubectl port-forward svc/anubis-debug 5003:5003 -n anubis
