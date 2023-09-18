# Debug
DEBUG_PERSISTENT_SERVICES := db traefik redis-master
DEBUG_RESTART_ALWAYS_SERVICES := api web-dev rpc-default rpc-theia rpc-regrade

# docker compose settings
DOCKER_COMPOSE ?= docker compose -p anubis
DOCKER_COMPOSE_PUSH_SERVICES := \
	api web \
	theia-init theia-autosave theia-autograde \
	theia-proxy theia-dockerd theia-autograde-docs

# K8S
#K8S_RESTART_DEPLOYMENTS := \
#	anubis-api anubis-web anubis-pipeline-api anubis-pipeline-poller anubis-theia-proxy \
#	anubis-rpc-default anubis-rpc-theia anubis-rpc-regrade \
#	anubis-theia-poller anubis-discord-bot anubis-theia-autograde-docs

# To tag docker images
GIT_TAG ?= $(shell git log -1 --pretty=%h)

# Anubis IDE variables
TRAEFIK_PORT := $(shell if [ "$$ANUBIS_IDE" = "1" ]; then echo 8000; else echo 80; fi)
ANUBIS_UID := $(shell if [ "$$ANUBIS_IDE" = "1" ]; then echo 1001; else echo 1000; fi)
DEV_URL := $(shell if [ "$$ANUBIS_IDE" = "1" ]; then echo "https://ide8000.anubis-lms.io"; else echo "http://localhost"; fi)
DOCKER_SOCK := $(shell if [ "$$ANUBIS_IDE" = "1" ]; then echo "/run/user/1001/docker.sock"; else echo "/var/run/docker.sock"; fi)

# Export make variables
export GIT_TAG
export TRAEFIK_PORT
export ANUBIS_UID
export DOCKER_SOCK

help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

startup-links:
	@echo ''
	@echo 'seed: $(DEV_URL)/api/admin/seed/'
	@echo 'auth: $(DEV_URL)/api/admin/auth/token/superuser'
	@echo 'auth: $(DEV_URL)/api/admin/auth/token/professor'
	@echo 'auth: $(DEV_URL)/api/admin/auth/token/ta'
	@echo 'auth: $(DEV_URL)/api/admin/auth/token/student'
	@echo 'site: $(DEV_URL)/'

.PHONY: context         # Grab kubectl and registry login from doctl
context:
	doctl kubernetes cluster kubeconfig save anubis2 --context anubis
	doctl registry login --context anubis

.PHONY: upgrade         # Helm upgrade Anubis k8s cluster
upgrade:
	helm upgrade --install anubis ./k8s/chart --set tag=$(GIT_TAG) -n anubis

.PHONY: restart         # Restart Anubis k8s cluster
restart:
	kubectl rollout restart -n anubis deploy \
		$(shell kubectl get deploy -n anubis -l app.kubernetes.io/name=anubis -o jsonpath='{.items[*].metadata.name}')

.PHONY: scalezero       # Scale all services to zero replicas (sometimes necessary for maintenance)
scalezero:
	kubectl scale deploy -n anubis --replicas 0 \
		$(shell kubectl get deploy -n anubis -l app.kubernetes.io/name=anubis -o jsonpath='{.items[*].metadata.name}')

.PHONY: deploy          # Deploy Anubis k8s cluster
deploy: build push upgrade

.PHONY: status          # See status of Anubis k8s cluster
status:
	helm status -n anubis anubis

.PHONY: build           # Build all docker images
build:
	$(DOCKER_COMPOSE) build --parallel --pull $(DOCKER_COMPOSE_PUSH_SERVICES)
	env GIT_TAG=latest $(DOCKER_COMPOSE) build --parallel --pull $(DOCKER_COMPOSE_PUSH_SERVICES)

.PHONY: push            # Push images to registry.digitalocean.com (requires vpn)
push: build
	$(DOCKER_COMPOSE) push $(DOCKER_COMPOSE_PUSH_SERVICES)
	env GIT_TAG=latest $(DOCKER_COMPOSE) push $(DOCKER_COMPOSE_PUSH_SERVICES)

.PHONY: pull            # Pull images from registry.digitalocean.com (requires vpn)
pull:
	#$(DOCKER_COMPOSE) pull $(DOCKER_COMPOSE_PUSH_SERVICES)
	env GIT_TAG=latest $(DOCKER_COMPOSE) pull $(DOCKER_COMPOSE_PUSH_SERVICES)

.PHONY: debug           # Start the cluster in debug mode
debug:
	$(DOCKER_COMPOSE) up -d $(DEBUG_PERSISTENT_SERVICES)
	$(DOCKER_COMPOSE) up \
		-d --force-recreate \
		$(DEBUG_RESTART_ALWAYS_SERVICES)
	@echo 'Waiting for db'
	@until mysqladmin -h 127.0.0.1 ping &> /dev/null; do sleep 1; done
	@echo 'running migrations'
	$(DOCKER_COMPOSE) exec api alembic upgrade head
	make startup-links

.PHONY: mindebug        # Setup mindebug environment
mindebug:
	@echo ''
	@echo 'seed: http://localhost:3000/api/admin/seed/'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/superuser'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/professor'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/ta'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/student'
	@echo 'site: http://localhost:3000/'
	make -j2 apirun webrun

.PHONY: mkdebug         # Start minikube debug
mkdebug:
	./k8s/debug/provision.sh
	make mkrestart startup-links

.PHONY: mkrestart       # Restart minikube debug
mkrestart:
	./k8s/debug/restart.sh

apirun:
	make -C api run

webrun:
	make -C web run

# Reset local docker compose db
yeetdb:
	$(DOCKER_COMPOSE) kill db
	$(DOCKER_COMPOSE) rm -f
	docker volume rm anubis_db_data
	$(DOCKER_COMPOSE) up -d --force-recreate db

theia-%:
	$(DOCKER_COMPOSE) pull $@

acme-backup:
	kubectl exec -it -n traefik -c traefik $(kubectl get pods -n traefik -o json | jq '.items[0].metadata.name' -r) -- cat data/acme.json > ../acme-$(date +%F).json
