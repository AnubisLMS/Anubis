#!/bin/sh

echo http://127.0.0.1:5001/
kubectl port-forward svc/kibana 5001:5601 -n anubis
