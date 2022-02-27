# https://docs.linuxserver.io/images/docker-webtop

ARG WEBTOP_TAG=ubuntu-xfce
FROM lscr.io/linuxserver/webtop:$WEBTOP_TAG

ENV TZ=America/New_York \
    PUID=1001 \
    GUID=1001 \
    KEYBOARD=en-us-qwerty \
    CUSTOM_PORT=5000

RUN set -ex; \
  apt update; \
  apt install git wget build-essential -y --no-install-recommends; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*; \
  mkdir -p /home/anubis; \
  chown -R 1001:1001 /home/anubis; \
  usermod -d /home/anubis abc; \
  cd /home/anubis; \
  sed -i 's/\/config/\/home\/anubis/g' $(find /defaults /etc/cont-init.d /etc/services.d -type f);
