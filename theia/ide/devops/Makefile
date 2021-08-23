
all: build

build:
	docker build \
		--build-arg version=latest \
		--build-arg strip=true \
		-t anubis-theia .

run:
	docker run \
		-it \
		-p 5000:5000 \
		-v "/home/jc/nyu/os/xv6-public:/home/project" \
		anubis-theia

debug:
	docker run \
		-it \
		-p 5000:5000 \
		-v "/home/jc/nyu/os/xv6-public:/home/project" \
		--entrypoint bash \
		anubis-theia
