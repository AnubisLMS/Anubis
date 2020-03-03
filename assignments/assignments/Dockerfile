FROM debian:stretch

RUN apt update \
  && apt install -y sudo qemu-system-x86 python3 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /mnt/

COPY ./entrypoint.sh /entrypoint.sh
COPY utils.py ./utils.py
RUN chmod +x /entrypoint.sh && chsh -s /bin/bash

CMD /entrypoint.sh

