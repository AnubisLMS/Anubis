# This docker image will install all the dependencies for the
# container to build xv6-public

FROM ubuntu:16.04

ENV TOOLPREFIX=""

RUN apt update \
  && apt install -y git \
                    make \
                    gcc \
                    libc6-i386 \
                    python3 \
                    python3-pip \
  && rm -rf /var/lib/apt/lists/* \
  && sudo pip3 install lorem

WORKDIR /mnt

COPY ./entrypoint.sh /entrypoint.sh
COPY overwrite.py /overwrite.py
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh
