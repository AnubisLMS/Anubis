#!/bin/sh

# Change into the directory that this script is in
cd $(dirname $0)
cd ..

# Stop if any command has an error
set -e

echo 'This script will provision a minikube cluster for debugging'

# Delete the minikube cluster if one exists
minikube delete

# Start a new minikube cluster
echo 'staring minikube...' 1>&2

# The minikube cluster needs significant resources. These lines calculate half the number of CPU cores,
# and half the RAM of the current machine. These are upper limits for the cluster, not reservations.
if uname -a | grep -i linux &> /dev/null; then
    # On linux, we can use the standard unix commands for
    # getting the core and memory resources
    CPUS=$(( $(nproc) / 2 ))
    MEM="$(( $(free -h | nice grep -i 'mem' | awk '{print substr($2, 1, length($2)-2)}') / 2 ))Gi"
else
    # On MacOS, we'll need to calculate the CPUs and cores
    # using sysctl. nproc and free are too cool for MacOS
    # apparently...
    CPUS=$(( $(sysctl -n hw.ncpu) / 2 ))
    MEM="$(( $(( $(sysctl -n hw.memsize) / 1048576 )) / 2 ))Mi"
fi

# The calico cni is super important for the minikube debugging. It is up
# to the networking layer to enforce any and all networking policies. The
# default minikube networking layer does not enforce this. To simulate prod
# networking, we need the calico networking layer.
#
# We are also mapping ports 80 and 443 from the minikube node to the host.
# This allows us to connect through traefik on https://localhost.
#
# The TTLAfterFinished feature gate allows us to specify a ttl for a finished
# kube job. This is nice as it allows us to clean up job resources
# automatically just by specifying something in the spec. How this isn't
# just a part of the v1 job spec is a wonder to me.
minikube start \
         --feature-gates=TTLAfterFinished=true \
         --ports=80:80,443:443 \
         --network-plugin=cni \
         --cpus=${CPUS} \
         --memory=${MEM} \
         --cni=calico

# Give the cluster a second
sleep 1

# Make sure kubectl is pointed at minikube
if ! kubectl config current-context | grep 'minikube' &> /dev/null; then
    echo 'Setting context to minikube' 1>&2
    kubectl config use-context minikube
fi

# Add a traefik=ingress label to the main minikube node. The traefik
# DaemonSet we install next relies on this label for scheduling.
echo 'Adding traefik ingress label to minikube node...'
kubectl label node minikube traefik=ingress --overwrite

# Install a basic traefik configuration. This was pretty much entirely
# pulled from the traefik documentation somewhere around traefik v2.1.
echo 'Adding traefik resources...'
kubectl create ns traefik
kubectl apply -f ./debug/traefik.yaml

# Add the external chart repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create the anubis namespace
kubectl create namespace anubis

# Create a minimal mariadb deployment in a mariadb namespace. On
# prod, the mariadb is in a seperate namespace, so we do the same
# here.
echo 'Adding mariadb'
helm upgrade --install mariadb bitnami/mariadb \
    --set 'auth.rootPassword=anubis' \
    --set 'volumePermissions.enabled=true' \
    --set 'auth.username=anubis' \
    --set 'auth.database=anubis' \
    --set 'auth.password=anubis' \
    --set 'fullnameOverride=anubis' \
    --set 'architecture=standalone' \
    --namespace anubis

# Install a minimal redis deployment
echo 'Adding redis'
helm upgrade --install redis bitnami/redis \
    --set fullnameOverride=redis \
    --set global.redis.password=anubis \
    --set architecture=standalone \
    --set master.persistence.enabled=false \
    --namespace anubis

if [ -f debug/init-secrets.sh ]; then
    bash debug/init-secrets.sh
fi

kubectl create secret generic api \
    --from-literal=database-uri=mysql+pymysql://anubis:anubis@mariadb.anubis.svc.cluster.local/anubis \
    --from-literal=database-host=mariadb.anubis.svc.cluster.local \
    --from-literal=database-password=anubis \
    --from-literal=redis-password=anubis \
    --from-literal=secret-key=$(head -c10 /dev/urandom | openssl sha1 -hex | awk '{print $2}') \
    --namespace anubis

# Create the oauth configuration secrets
kubectl create secret generic oauth \
    --from-literal=consumer-key='aaa' \
    --from-literal=consumer-secret='aaa' \
    --namespace anubis

# Run the debug.sh script to build, then install all the stuff
# for anubis.
exec ./debug/restart.sh
