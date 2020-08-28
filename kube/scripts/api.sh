#!/bin/sh

kubectl port-forward svc/anubis 5000:5000 -n anubis
