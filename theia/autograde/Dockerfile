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
VOLUME /log

COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY supervisord.conf /supervisord.conf
COPY . /opt/anubis/anubis_autograde

RUN set -eux; \
    pip3 install --no-cache-dir /opt/anubis/anubis_autograde; \
    rm -rf /opt/anubis/anubis_autograde

USER anubis
CMD ["/docker-entrypoint.sh"]


