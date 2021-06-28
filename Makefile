PERSISTENT_SERVICES := db traefik kibana elasticsearch-coordinating redis-master
RESTART_ALWAYS_SERVICES := api web-dev rpc-default rpc-theia rpc-regrade
PUSH_SERVICES := api web theia-init theia-proxy theia-admin theia-xv6

help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

startup-links:
	@echo ''
	@echo 'seed: http://localhost/api/admin/seed/'
	@echo 'auth: http://localhost/api/admin/auth/token/superuser'
	@echo 'auth: http://localhost/api/admin/auth/token/ta'
	@echo 'auth: http://localhost/api/admin/auth/token/professor'
	@echo 'site: http://localhost/'

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
	docker-compose up -d traefik db redis-master
	docker-compose up \
		-d --force-recreate \
		api web-dev rpc-default
	@echo 'Waiting a moment before running migrations'
	sleep 3
# 	@echo 'running migrations'
# 	make -C api migrations
	make startup-links

.PHONY: debug-mk     # Start minikube debug
debug-mk:
	./k8s/debug/provision.sh
	make startup-links

.PHONY: restart-mk   # Restart minikube debug
restart-mk:
	./k8s/debug/restart.sh
	make startup-links

yeetdb:
	docker-compose kill db
	docker-compose rm -f
	docker volume rm anubis_db_data
	docker-compose up -d --force-recreate db
