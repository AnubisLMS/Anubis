PERSISTENT_SERVICES := db traefik kibana elasticsearch-coordinating redis-master logstash
RESTART_ALWAYS_SERVICES := api web-dev rpc-default rpc-theia rpc-regrade
PUSH_SERVICES := api web theia-init theia-proxy theia-admin theia-xv6



CURRENT_DIR := $(shell basename $$(pwd) | tr '[:upper:]' '[:lower:]')
IMAGES := $(shell \
	ruby -ryaml -rjson -e 'puts JSON.pretty_generate(YAML.load(ARGF))' \
	docker-compose.yml | jq '.services | .[].image | select(.!=null)' -r \
	2> /dev/null \
)
BUILT_IMAGES := $(shell \
	docker image ls | \
	awk '{print $$1}' | \
	grep -P '^($(CURRENT_DIR)_|os3224-)' \
	2> /dev/null \
)
RUNNING_CONTAINERS := $(shell docker-compose ps -q)
VOLUMES := $(shell docker volume ls | awk '{if (match($$2, /^anubis_.*$$/)) {print $$2}}')


help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: deploy       # Deploy Anubis to cluster
deploy:
	./k8s/deploy.sh
	./k8s/restart.sh

.PHONY: build        # Build all docker images
build:
	docker-compose build --parallel --pull

.PHONY: push         # Push images to registry.digitalocean.com (requires vpn)
push:
	docker-compose build --parallel --pull $(PUSH_SERVICES)
	docker-compose push $(PUSH_SERVICES)

startup-links:
	@echo ''
	@echo 'seed: http://localhost/api/admin/seed/'
	@echo 'auth: http://localhost/api/admin/auth/token/superuser'
	@echo 'auth: http://localhost/api/admin/auth/token/ta'
	@echo 'auth: http://localhost/api/admin/auth/token/professor'
	@echo 'site: http://localhost/'

.PHONY: debug        # Start the cluster in debug mode
debug:
	docker-compose up -d $(PERSISTENT_SERVICES)
	docker-compose up \
		-d --force-recreate \
		$(RESTART_ALWAYS_SERVICES)
	@echo 'Waiting a moment before running migrations'
	sleep 3
	@echo 'running migrations'
	make -C api migrations
	make startup-links

.PHONY: mindebug     # Start the minimal cluster in debug mode
mindebug:
	docker-compose up -d traefik db redis-master logstash
	docker-compose up \
		-d --force-recreate \
		api web-dev rpc-default rpc-theia
	@echo 'Waiting a moment before running migrations'
	sleep 3
	@echo 'running migrations'
	make -C api migrations
	make startup-links

.PHONY: mkdebug      # Start minikube debug
mkdebug:
	./k8s/debug/provision.sh
	make startup-links

.PHONY: mkrestart    # Restart minikube debug
mkrestart:
	./k8s/debug/restart.sh
	make startup-links

yeetdb:
	docker-compose kill db
	docker-compose rm -f
	docker volume rm anubis_db_data
	docker-compose up -d --force-recreate db

.PHONY: clean        # Clean up volumes, images and data
clean:
	docker-compose kill
	if [ -n "$(RUNNING_CONTAINERS)" ]; then \
		docker rm -f $(RUNNING_CONTAINERS); \
	fi
	if [ -n "$(IMAGES)" ]; then \
		docker rmi -f $(IMAGES); \
	fi
	if [ -n "$(BUILT_IMAGES)" ]; then \
		docker rmi -f $(BUILT_IMAGES); \
	fi
	if [ -n "${VOLUMES}" ]; then \
		docker volume rm $(VOLUMES); \
	fi
	docker system prune -f
