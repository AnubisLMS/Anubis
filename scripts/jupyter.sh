#!/bin/sh

kubectl logs -l app=debug -c jupyter -n anubis
kubectl port-forward svc/debug 5003:5003 -n anubis
