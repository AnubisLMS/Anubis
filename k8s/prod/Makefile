##################################
#
# Copyright John Cunniff 2021
#
# Anubis Production Provisioning Makefile
#  - Use this script to provision your very
#    own Anubis cluster.
#  - There are some assumptions that I am making
#    with this script:
#    - I assume that you have: kubectl, helm3,
#      and openssl installed. I also assume
#      that this is running on a unix command
#      line.
#    - Another big assumption that we are making
#      is that this is a fresh k8s cluster that
#      we are installing on. This script will do
#      things like change the default storage
#      class to longhorn. Change this if you need.
#    - There are also a couple places (primarily
#      in the elk configuration) that specifies
#      do-block-storage for pvc storage classes.
#      This is the default storage-class on digital
#      ocean. In the future I would like to remove
#      this assumption and have this be a Makefile
#      variable in this file.
#
#
# TODO remove do-block-storage assumptions from the elk
#      yaml configurations
#
##################################



SERVICES := api web theia-init theia-proxy theia-admin theia-xv6


# There are a few assumptions here. I'm assuming that if this is run on
# a Mac that /dev/random exists (no idea if it does, I don't like apple).
# I am also making the assumption that openssl is installed and available
# on the command line. I also assume this just would not work on windows
# powershell (but like what even does).
SECRET_KEY := "$(shell head -c10 /dev/random | openssl sha1 -hex | awk '{print $$2}')"
DB_PASS := "$(shell head -c10 /dev/random | openssl sha1 -hex | awk '{print $$2}')"
REDIS_PASS := "$(shell head -c10 /dev/random | openssl sha1 -hex | awk '{print $$2}')"

ELASTIC_VERSION := 7.12


all: \
	helm-init \
	traefik \
	elasticsearch \
	filebeat \
	mariadb \
	redis \
	longhorn \
	api-secret \
	build \
	push \
	echo-passes

ns-%:
	if ! kubectl get namespace $*; then \
		kubectl create namespace $*; \
	fi

echo-passes:
	@echo
	@echo "  Generated passwords (not updated if upgrade)"
	@echo "  SECRET_KEY = $(SECRET_KEY)"
	@echo "  DB_PASS    = $(DB_PASS)"
	@echo "  REDIS_PASS = $(REDIS_PASS)"
	@echo

helm-init:
	helm repo add traefik 'https://helm.traefik.io/traefik'
	helm repo add bitnami 'https://charts.bitnami.com/bitnami'
	helm repo add elastic 'https://helm.elastic.co'
	helm repo add longhorn 'https://charts.longhorn.io'
	helm repo update

traefik: ns-traefik
	helm upgrade \
		--install traefik traefik/traefik \
		--values traefik-values.yaml \
		--namespace traefik

# We need the default storage class to
# be longhorn (or really any class that
# supports ReadWriteMany filesystems) to
# make the theia pods work properly.
longhorn: ns-longhorn-system
	helm upgrade \
		--install longhorn longhorn/longhorn \
    --namespace longhorn-system
	kubectl patch storageclass longhorn \
		-p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

elasticsearch: ns-elastic
	helm upgrade \
		--install elasticsearch elastic/elasticsearch \
		--values elastic-values.yaml \
		--version $(ELASTIC_VERSION) \
		--namespace elastic

filebeat:
	helm upgrade \
		--install filebeat elastic/filebeat \
		--values filebeat-values.yaml \
		--version $(ELASTIC_VERSION) \
		--namespace kube-system

mariadb: ns-mariadb
	helm upgrade --install mariadb bitnami/mariadb \
		--set 'volumePermissions.enabled=true' \
		--set 'auth.username=anubis' \
		--set 'auth.database=anubis' \
		--set "auth.password=$(DB_PASS)" \
		--set 'replication.enabled=false' \
		--namespace mariadb

redis: ns-anubis
	helm upgrade \
		--install redis bitnami/redis \
		--set fullnameOverride=redis \
		--set global.redis.password=$(REDIS_PASS) \
		--set architecture=standalone \
		--set master.persistence.enabled=false \
		--namespace anubis

api-secret:
	@if ! kubectl get secret api -n anubis; then;
		kubectl create secret generic api \
			--namespace anubis \
			--from-literal=database-uri=mysql+pymysql://anubis:$(DB_PASS)@mariadb.mariadb.svc.cluster.local/anubis \
			--from-literal=database-password=$(DB_PASS) \
			--from-literal=redis-password=$(REDIS_PASS) \
			--from-literal=secret-key=$(SECRET_KEY); \
	fi

# Add any extra kubectl create secret commands
# to a script called init-secrets.sh in this directory.
# It will be run here when provisioning.
init-secrets:
	if [ -f init-secrets.sh ]; then \
		./init-secrets.sh; \
	fi

# Build a fresh version of all the core service images
#   - The Theia images may make this step take a while
#     (depends on if you are on a potato).
build:
	(cd ../../ && docker-compose build --no-cache --parallel --pull $(SERVICES))

# Push the freshly built service images
#   - Again, the Theia service images may be 1-2GiB, which
#     may make this step take a while if you are on slow
#     internet.
push:
	(cd ../../ && docker-compose push $(SERVICES))
