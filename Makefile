PERSISTENT_SERVICES := db traefik redis-master
RESTART_ALWAYS_SERVICES := api old-web-dev web-dev rpc-default rpc-theia rpc-regrade
PUSH_SERVICES := api old-web puller theia-init theia-proxy
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

.PHONY: build-ides   # Build all ide docker images
build-ides:
	docker-compose build --parallel --pull $(THEIA_IDES)

.PHONY: push-ides    # Push ide images to registry.digitalocean.com (requires vpn)
push-ides:
	docker-compose push $(THEIA_IDES)

.PHONY: prop-ides    # Create theia-prop daemonset to propigate latest ide images
prop-ides:
	kubectl apply -f theia/ide/theia-prop.yaml
	kubectl rollout restart ds theia-prop

.PHONY: debug        # Start the cluster in debug mode
debug:
	docker-compose up -d $(PERSISTENT_SERVICES)
	docker-compose up \
		-d --force-recreate \
		$(RESTART_ALWAYS_SERVICES)
	@echo 'Waiting for db'
	@until mysqladmin -h 127.0.0.1 ping &> /dev/null; do sleep 1; done
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
	yarn
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
