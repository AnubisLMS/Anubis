#!/bin/sh


echo https://127.0.0.1:8443/
kubectl -n kubernetes-dashboard describe secret admin-user-token | grep ^token
kubectl port-forward service/kubernetes-dashboard 8443:443 -n kubernetes-dashboard
