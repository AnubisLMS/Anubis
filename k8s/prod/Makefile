

BUILD_SERVICES := api web theia-init theia-proxy theia-admin theia-xv6
SECRET_KEY := "$(head -c10 /dev/random | openssl sha1 -hex | awk '{print $2}')"
DB_PASS := "$(head -c10 /dev/random | openssl sha1 -hex | awk '{print $2}')"
REDIS_PASS := "$(head -c10 /dev/random | openssl sha1 -hex | awk '{print $2}')"


all: helm-init traefik elasticsearch mariadb redis longhorn api-secret build push

ns-%:
	if ! kubectl get namespace $*; then \
		kubectl create namespace $*; \
	fi

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
		--version 7.12 \
		--namespace elastic

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
	if ! kubectl get secret api -n anubis; then;
		kubectl create secret generic api \
			--namespace anubis \
			--from-literal=database-uri=mysql+pymysql://anubis:$(DB_PASS)@mariadb.mariadb.svc.cluster.local/anubis \
			--from-literal=database-password=$(DB_PASS) \
			--from-literal=redis-password=$(REDIS_PASS) \
			--from-literal=secret-key=$(SECRET_KEY); \
	fi

init-secrets:
	if [ -f init-secrets.sh ]; then \
		./init-secrets.sh; \
	fi

build:
	(cd ../../ && docker-compose build --parallel --pull $(BUILD_SERVICES))

push:
	(cd ../../ && docker-compose push $(BUILD_SERVICES))
