#!/bin/sh

kubectl -n kubernetes-dashboard describe secret admin-user-token | grep ^token
echo https://127.0.0.1:8443/
kubectl port-forward service/kubernetes-dashboard 8443:443 -n kubernetes-dashboard
