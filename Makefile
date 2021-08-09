PERSISTENT_SERVICES := db traefik redis-master
RESTART_ALWAYS_SERVICES := api web-dev rpc-default rpc-theia rpc-regrade
PUSH_SERVICES := api web puller theia-init theia-proxy theia-admin theia-xv6

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
	docker-compose exec api alembic upgrade head
	make startup-links

.PHONY: mindebug     # Setup mindebug environment
mindebug:
	@echo ''
	@echo 'seed: http://localhost:3000/api/admin/seed/'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/superuser'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/professor'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/ta'
	@echo 'auth: http://localhost:3000/api/admin/auth/token/student'
	@echo 'site: http://localhost:3000/'
	make -j2 apirun webrun

apirun:
	make -C api run

webrun:
	make -C web run

.PHONY: mkdebug     # Start minikube debug
mkdebug:
	./k8s/debug/provision.sh

.PHONY: restart-mk   # Restart minikube debug
restart-mk:
	./k8s/debug/restart.sh
	make startup-links

yeetdb:
	docker-compose kill db
	docker-compose rm -f
	docker volume rm anubis_db_data
	docker-compose up -d --force-recreate db
