# Debug
DEBUG_PERSISTENT_SERVICES := db traefik redis-master
DEBUG_RESTART_ALWAYS_SERVICES := api web-dev old-web-dev rpc-default rpc-theia rpc-regrade

# docker-compose settings
DOCKER_COMPOSE_PUSH_SERVICES := api web old-web theia-init theia-proxy

# K8S
K8S_RESTART_DEPLOYMENTS := \
	anubis-api anubis-web anubis-old-web anubis-pipeline-api anubis-theia-proxy anubis-rpc-default anubis-rpc-theia \
  anubis-rpc-regrade anubis-theia-poller anubis-discord-bot

# Theia IDES
THEIA_BASE_IDE := theia-base-397 theia-base-3100
THEIA_IDES := theia-xv6 theia-admin theia-devops theia-jepst theia-distributed-systems theia-software-engineering


help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

startup-links:
	@echo ''
	@echo 'seed: http://localhost/api/admin/seed/'
	@echo 'auth: http://localhost/api/admin/auth/token/superuser'
	@echo 'auth: http://localhost/api/admin/auth/token/professor'
	@echo 'auth: http://localhost/api/admin/auth/token/ta'
	@echo 'auth: http://localhost/api/admin/auth/token/student'
	@echo 'site: http://localhost/'


.PHONY: upgrade        # Helm upgrade Anubis k8s cluster
upgrade:
	helm upgrade --install anubis ./k8s/chart -n anubis

.PHONY: restart        # Restart Anubis k8s cluster
restart:
	kubectl rollout restart -n anubis deploy \
		$(K8S_RESTART_DEPLOYMENTS)

.PHONY: deploy         # Deploy Anubis k8s cluster
deploy: build push upgrade restart

.PHONY: build          # Build all docker images
build:
	docker-compose build --parallel --pull $(DOCKER_COMPOSE_PUSH_SERVICES)

.PHONY: push           # Push images to registry.digitalocean.com (requires vpn)
push: build
	docker-compose push $(DOCKER_COMPOSE_PUSH_SERVICES)

.PHONY: build-ides     # Build all ide docker images
build-ides:
	@echo 'building base images'
	docker-compose build --parallel --pull $(THEIA_BASE_IDE)

	@echo 'building ide image'
	docker-compose build --parallel $(THEIA_IDES)

.PHONY: push-base-ides # Push base ide images to registry.digitalocean.com
push-base-ides:
	docker-compose push $(THEIA_BASE_IDE)

.PHONY: push-ides      # Push ide images to registry.digitalocean.com
push-ides:
	docker-compose push $(THEIA_IDES)

.PHONY: prop-ides      # Create theia-prop daemonset to propagate latest ide images
prop-ides:
	kubectl apply -f theia/ide/theia-prop.yaml
	kubectl rollout restart ds theia-prop

.PHONY: debug          # Start the cluster in debug mode
debug:
	docker-compose up -d $(DEBUG_PERSISTENT_SERVICES)
	docker-compose up \
		-d --force-recreate \
		$(DEBUG_RESTART_ALWAYS_SERVICES)
	@echo 'Waiting for db'
	@until mysqladmin -h 127.0.0.1 ping &> /dev/null; do sleep 1; done
	@echo 'running migrations'
	docker-compose exec api alembic upgrade head
	make startup-links

.PHONY: mindebug       # Setup mindebug environment
mindebug:
	@echo ''
	@echo 'seed: http://localhost:3000/api/admin/seed/'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/superuser'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/professor'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/ta'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/student'
	@echo 'site: http://localhost:3000/'
	make -j2 apirun webrun

.PHONY: mkdebug        # Start minikube debug
mkdebug:
	./k8s/debug/provision.sh

apirun:
	make -C api run

webrun:
	make -C web run

# Reset local docker-compose db
yeetdb:
	docker-compose kill db
	docker-compose rm -f
	docker volume rm anubis_db_data
	docker-compose up -d --force-recreate db
