FROM docker:20.10-dind-rootless

# Docker cannot work off of nfs
# https://github.com/docker/for-linux/issues/1172

ENV DOCKER_HOST="tcp://localhost:2376" \
    DOCKER_TLS_CERTDIR="/certs" \
    DOCKER_TLS_VERIFY="1" \
    DOCKER_CERT_PATH="/certs/client" \
    ANUBIS_RUN_DOCKERD="0" \
    HOME="/home/docker"

USER 0
RUN set -eux; \
    adduser -D -u 1001 -h /home/docker anubis; \
    apk add --no-cache supervisor; \
    sed -i 's/rootless/anubis/' /etc/subuid /etc/subgid;

VOLUME /certs

COPY supervisord.conf /
COPY dockerd.sh /anubis/

USER 1001
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
