FROM python:3.13-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /requirements.txt
RUN set -eux; \
    useradd -m --user-group --uid 1001 anubis; \
    apt update;  \
    apt install -y --no-install-recommends git bash g++; \
    pip3 install --no-cache-dir -r /requirements.txt; \
    mkdir -p /opt/anubis; \
    chmod 755 /opt/anubis; \
    chown anubis:anubis /opt/anubis; \
    rm -rf /usr/share/doc; \
    rm -rf /usr/local/share/.cache; \
    rm -rf /var/cache/apt/*; \
    rm -rf /var/lib/apt/lists/*

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


