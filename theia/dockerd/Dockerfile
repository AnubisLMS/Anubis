FROM docker:20.10-dind-rootless

ENV DOCKER_HOST="tcp://localhost:2376" \
    DOCKER_TLS_CERTDIR="/certs" \
    DOCKER_TLS_VERIFY="1" \
    DOCKER_CERT_PATH="/certs/client" \
    ANUBIS_RUN_DOCKERD="0"

USER 0
RUN set -eux; \
    adduser -D -u 1001 theia; \
    apk add --no-cache supervisor; \
    sed -i 's/rootless/theia/' /etc/subuid /etc/subgid;

VOLUME /certs

COPY supervisord.conf /
COPY dockerd.sh /anubis/

USER 1001
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
