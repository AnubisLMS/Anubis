FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /requirements.txt
RUN set -eux; \
    useradd -M anubis; \
    apt update;  \
    apt install -y --no-install-recommends git bash g++; \
    pip3 install --no-cache-dir -r /requirements.txt; \
    mkdir -p /opt/anubis; \
    chmod 755 /opt/anubis; \
    chown anubis:anubis /opt/anubis; \
    apt autoremove -y; \
    env USER=root find /opt/anubis -depth \
    \( \
    \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
    -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
    \) -exec rm -rf '{}' + ; \
    \
    env USER=root find /usr/local -depth \
    \( \
    \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
    -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
    \) -exec rm -rf '{}' + ; \
    rm -rf /usr/share/doc; \
    rm -rf /usr/lib/gcc; \
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


