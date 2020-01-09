# This docker image will install all the dependencies for the
# container to build xv6-public

FROM ubuntu:14.04

ENV TOOLPREFIX=""

RUN apt update \
  && apt install -y make gcc libc6-i386 qemu-system-x86 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

COPY ./build.sh /usr/local/bin/build.sh
RUN chmod +x /usr/local/bin/build.sh
