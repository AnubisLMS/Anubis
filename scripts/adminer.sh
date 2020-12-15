#!/bin/sh

echo http://127.0.0.1:5002/
kubectl port-forward svc/debug 5002:5002 -n anubis
