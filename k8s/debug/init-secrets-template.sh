#!/bin/sh

# COPY the content to init-secrets.sh and configure the secrets before deployment.
# The file will be gitignored, but be extra sure you do not commit it on accident.

# Create the api configuration secrets
kubectl create secret generic api \
    --from-literal=database-uri=mysql+pymysql://anubis:anubis@mariadb.anubis.svc.cluster.local/anubis \
    --from-literal=database-host=mariadb.anubis.svc.cluster.local \
    --from-literal=database-password=anubis \
    --from-literal=database-port=3306 \
    --from-literal=redis-password=anubis \
    --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
    --namespace anubis

# Create the oauth configuration secrets
kubectl create secret generic oauth \
    --from-literal=consumer-key='aaa' \
    --from-literal=consumer-secret='aaa' \
    --namespace anubis

# Create the git user secrets
kubectl create secret generic git \
    --from-literal=token='token' \
    --from-literal=credentials='https://your-robot:token@github.com' \
    --namespace anubis
