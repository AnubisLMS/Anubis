
CURRENT_DIR := $(shell dirname $(PWD))

IMAGES := $(shell \
	ruby -ryaml -rjson -e 'puts JSON.pretty_generate(YAML.load(ARGF))' \
	docker-compose.yml | jq '.services | .[].image | select(.!=null)'  -r)

BUILT_IMAGES := $(shell \
	docker image ls | awk 'count=0 {count+=1; if (count > 1) {print $1}}' | grep -P '^$(CURRENT_DIR)_')

RUNNING_CONTAINERS := $(shell docker-compose ps -q)


all: check debug

check:
	@for var in ACME_EMAIL MYSQL_ROOT_PASSWORD AUTH DOMAIN; do \
		if [ -f .env ] && grep -p "^${var}=" .env &> /dev/null || [ ! -z "${var}" ]; then \
			echo "ERROR ${var} not defined! this variable is required" 1>&2; \
		fi; \
	done

build:
	docker-compose build --pull --parallel

debug: build
	docker-compose up -d traefik redis db
	docker-compose up -d --force-recreate --scale worker=3 api worker

deploy: build
	docker-compose -f ./docker-compose.yml up -d traefik redis db
	docker-compose -f ./docker-compose.yml up -d --force-recreate --scale worker=3 api worker

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
