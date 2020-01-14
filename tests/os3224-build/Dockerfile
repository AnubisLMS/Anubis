# This docker image will install all the dependencies for the
# container to build xv6-public

FROM ubuntu:16.04

ENV TOOLPREFIX=""

RUN apt update \
  && apt install -y git \
                    make \
                    gcc \
                    libc6-i386 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /mnt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh
