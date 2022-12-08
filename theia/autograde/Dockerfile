FROM python:3.10-alpine

COPY requirements.txt /requirements.txt
RUN set -eux; \
    adduser -D -u 1001 -h /home/anubis anubis; \
    apk add --update --no-cache git bash; \
    pip3 install --no-cache-dir -r /requirements.txt; \
    mkdir /opt/anubis; \
    chmod 755 /opt/anubis; \
    chown anubis:anubis /opt/anubis

VOLUME /home/anubis

COPY supervisord.conf /supervisord.conf
COPY anubis_autograde /opt/app/autograde

USER anubis
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]


