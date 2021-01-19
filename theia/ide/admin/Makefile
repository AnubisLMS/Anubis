
all: build

build:
	docker build -t anubis-theia .

run:
	docker run \
		-it \
		-p 5000:5000 \
		-v "/home/jc/nyu/os/assignment-tests:/home/project" \
		--privileged \
		anubis-theia

debug:
	docker run \
		-it \
		-p 5000:5000 \
		-v "/home/jc/nyu/os/assignment-tests:/home/project" \
		--entrypoint bash \
		anubis-theia
