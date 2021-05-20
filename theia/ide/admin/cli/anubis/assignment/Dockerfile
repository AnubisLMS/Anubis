FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN set -ex; apt update \
  && apt install -y git python3 python3-pip qemu-system-x86 \
  && pip3 install --no-cache-dir pyyaml requests gitpython parse lorem \
  && apt autoremove -y \
  && find / -name .cache -exec 'rm' '-rf' '{}' ';' \
  && rm -rf /var/cache/apt/* \
  && rm -rf /var/lib/apt/lists/* \
  && useradd --no-create-home -u 1001 student \
  && mkdir -p /root/anubis/student \
  && chmod 700 -R /root \
  && chown student:student /root/anubis/student
WORKDIR /root/anubis

COPY pipeline.py utils.py meta.yml /root/anubis/
COPY assignment.py assignment.py
# COPY student /student

CMD python3 pipeline.py
