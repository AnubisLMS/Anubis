FROM debian:stretch

RUN apt update \
  && apt install -y qemu-system-x86 python3 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /mnt/

COPY ./entrypoint.sh /entrypoint.sh
COPY utils.py /mnt/utils.py
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh

