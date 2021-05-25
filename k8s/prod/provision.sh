#!/bin/sh

# Change into the directory that this script is in
cd $(dirname $0)

# Add the bitnami helm charts
helm repo add traefik https://helm.traefik.io/traefik
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add elastic https://helm.elastic.co
helm repo add longhorn https://charts.longhorn.io
helm repo update

kubectl create ns traefik
kubectl create ns longhorn-system
kubectl create ns elastic
kubectl create ns anubis


SECRET_KEY="$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}')"
DB_PASS="$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}')"
REDIS_PASS="$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}')"

echo 'Adding traefik'
helm upgrade \
     --install traefik traefik/traefik \
     --namespace traefik \
     --create-namespace \
     --values traefik-values.yaml

echo 'Adding longhorn'
helm install longhorn/longhorn \
     --name longhorn \
     --namespace longhorn-system

# Create a minimal mariadb deployment in a mariadb namespace. On
# prod, the mariadb is in a seperate namespace, so we do the same
# here.
echo 'Adding mariadb'
kubectl create namespace mariadb
helm upgrade --install mariadb bitnami/mariadb \
    --set 'auth.rootPassword=anubis' \
    --set 'volumePermissions.enabled=true' \
    --set 'auth.username=anubis' \
    --set 'auth.database=anubis' \
    --set "auth.password=${DB_PASS}" \
    --set 'replication.enabled=false' \
    --namespace mariadb

# Install a minimal elasticsearch and kibana deployments
echo 'Adding elasticsearch'
kubectl create namespace anubis
helm upgrade \
     --version 7.12 \
		 --install elasticsearch elastic/elasticsearch \
		 --create-namespace \
		 --set replicas=1 \
		 --set resources=null \
		 --set volumeClaimTemplate.resources.requests.storage=8Gi \
     --set volumeClaimTemplate.storageClassName=do-block-storage \
		 --namespace elastic

# Install a minimal redis deployment
echo 'Adding redis'
helm upgrade --install redis bitnami/redis \
    --set fullnameOverride=redis \
    --set global.redis.password=${REDIS_PASS} \
    --set architecture=standalone \
    --set master.persistence.enabled=false \
    --namespace anubis

# Create api secret
kubectl create secret generic api -n anubis \
        --from-literal=database-uri=mysql+pymysql://anubis:${DB_PASS}@mariadb.mariadb.svc.cluster.local/anubis \
        --from-literal=database-password=${DB_PASS} \
        --from-literal=redis-password=${REDIS_PASS} \
        --from-literal=secret-key=${SECRET_KEY}


if [ -f ./init-secrets.sh ]; then
    bash ./init-secrets.sh
fi

cd ../../
docker-compose build --parallel --pull
docker-compose push api web theia-init theia-proxy theia-admin theia-xv6
