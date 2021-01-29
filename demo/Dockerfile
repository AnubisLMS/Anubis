FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
  && apt install -y git python3 python3-pip qemu-system-x86 \
  && pip3 install pyyaml requests gitpython parse lorem
RUN useradd --no-create-home -u 1001 student \
  && mkdir -p /root/anubis/student \
  && chmod 700 -R /root \
  && chown student:student /root/anubis/student
WORKDIR /root/anubis

COPY pipeline.py pipeline.py
COPY utils.py utils.py
COPY assignment.py assignment.py
COPY meta.yml meta.yml

CMD python3 pipeline.py
