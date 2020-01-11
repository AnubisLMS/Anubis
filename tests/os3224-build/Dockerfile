# This docker image will install all the dependencies for the
# container to build xv6-public

FROM ubuntu:14.04

ENV TOOLPREFIX=""

RUN apt update \
  && apt install -y git \
                    make \
                    gcc \
                    libc6-i386 \
                    qemu-system-x86 \
                    python3 \
                    python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh
