
# These variables control the number of instances of the api and
# the rq workers get created. Take care to gradually move these values
# up, and not to overload your system.
#
# RQ_WORKER_SCALE will be the max number of assignments anubis can process
# at any given time.
API_SCALE := 3
RQ_WORKER_SCALE := 5


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

API_IP := $(shell docker network inspect traefik-proxy | \
	jq '.[0].Containers | .[] | select(.Name == "anubis_api_1") | .IPv4Address' -r | \
	awk '{print substr($$0, 1, index($$0, "/")-1)}' \
	2> /dev/null \
)

VOLUMES := $(shell docker volume ls | awk '{if (match($$2, /^anubis_.*$$/)) {print $$2}}')

PERSISTENT_SERVICES := db traefik kibana elasticsearch redis smtp
RESTART_ALWAYS_SERVICES := api worker web
BOMBLAB_SERVICES := bomblab-report bomblab-request bomblab-result bomblab-bombs

help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: check        # Checks that env vars are set
check:
	for var in ACME_EMAIL MYSQL_ROOT_PASSWORD AUTH DOMAIN; do \
		if ([ -f .env ] && ! grep -P "^$${var}=" .env &> /dev/null) && [ ! -z "$${var}" ]; then \
			echo "ERROR $${var} not defined! this variable is required" 1>&2; \
		fi; \
	done

.PHONY: build        # Build all docker images
build:
	docker-compose build --pull --parallel
	./assignments/build.sh

.PHONY: db           # Start and initialize the database service
db:
	docker-compose up -d db
	until docker-compose exec db mysqladmin ping -u root; do sleep 1; done
	@sleep 1
	@docker-compose exec db \
		sh -c 'mysql -u root < /docker-entrypoint-initdb.d/init.sql' || true
	@docker-compose exec db \
		sh -c 'mysql -u root --password=password < /docker-entrypoint-initdb.d/init.sql' || true

.PHONY: debug        # Start the cluster in debug mode
debug: check build db
	docker-compose up -d $(PERSISTENT_SERVICES)
	docker-compose up \
		-d --force-recreate \
		--scale worker=3 \
		--scale api=1 \
		$(RESTART_ALWAYS_SERVICES) \
		$(BOMBLAB_SERVICES)

.PHONY: deploy       # Start the cluster in production mode
deploy: check build db restart

.PHONY: bomblab
bomblab:
	docker-compose -f ./docker-compose.yml up \
		-d --force-recreate \
		$(BOMBLAB_SERVICES)

.PHONY: restart      # Restart the cluster
restart:
	docker-compose -f ./docker-compose.yml up -d $(PERSISTENT_SERVICES)
	docker-compose -f ./docker-compose.yml up \
		-d --force-recreate \
		--scale worker=$(RQ_WORKER_SCALE) \
		--scale api=$(API_SCALE) \
		$(RESTART_ALWAYS_SERVICES) \

.PHONY: cli          # Install the cli
cli:
	sudo pip3 install ./cli

.PHONY: backup       # Backup database to file
backup:
	./scripts/backup.sh

.PHONY: restore      # Restore to most recent backup
restore:
	./scripts/restore.sh

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
