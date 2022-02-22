# https://docs.linuxserver.io/images/docker-webtop

ARG WEBTOP_TAG=ubuntu-xfce
FROM lscr.io/linuxserver/webtop:$WEBTOP_TAG

ENV TZ=America/New_York \
    PUID=1001 \
    GUID=1001 \
    KEYBOARD=en-us-qwerty
    #SUBFOLDER=/ide


RUN set -ex; \
  mkdir -p /home/anubis; \
  chown -R 1001:1001 /home/anubis; \
  usermod -d /home/anubis abc; \
  cd /home/anubis; \
  sed -i 's/\/config/\/home\/anubis/g' $(find /defaults /etc/cont-init.d /etc/services.d -type f);
