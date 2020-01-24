
CURRENT_DIR := $(shell dirname $(PWD))

IMAGES := $(shell \
	ruby -ryaml -rjson -e 'puts JSON.pretty_generate(YAML.load(ARGF))' \
	docker-compose.yml | jq '.services | .[].image | select(.!=null)' -r \
	2> /dev/null \
)

BUILT_IMAGES := $(shell \
	docker image ls | \
	awk 'count=0 {count+=1; if (count > 1) {print $1}}' | \
	grep -P '^$(CURRENT_DIR)_'\
	2> /dev/null \
)

RUNNING_CONTAINERS := $(shell docker-compose ps -q)

API_IP := $(shell docker network inspect traefik-proxy | \
	jq '.[0].Containers | .[] | select(.Name == "anubis_api_1") | .IPv4Address' -r | \
	awk '{print substr($$0, 1, index($$0, "/")-1)}' \
	2> /dev/null \
)

VOLUMES := $(shell docker volume ls | awk '{if (match($$2, /^anubis_.*$$/)) {print $$2}}')


all: check debug

check:
	@for var in ACME_EMAIL MYSQL_ROOT_PASSWORD AUTH DOMAIN; do \
		if [ -f .env ] && grep -p "^${var}=" .env &> /dev/null || [ ! -z "${var}" ]; then \
			echo "ERROR ${var} not defined! this variable is required" 1>&2; \
		fi; \
	done

build:
	docker-compose build --pull --parallel
	./tests/build.sh

.PHONY: db
db:
	docker-compose up -d db
	until docker-compose exec db mysqladmin ping -u root; do sleep 1; done
	@sleep 1
	docker-compose exec db sh -c 'mysql -u root < /docker-entrypoint-initdb.d/init.sql'

debug: build db
	docker-compose up -d traefik redis smtp
	docker-compose up -d --force-recreate --scale worker=3 api worker

deploy: build db
	docker-compose -f ./docker-compose.yml up -d traefik redis smtp
	docker-compose -f ./docker-compose.yml up -d --force-recreate --scale worker=3 api worker

test:
	curl "http://$(API_IP):5000/public/test"

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
