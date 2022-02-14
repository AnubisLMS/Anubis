ARG PY_VERSION=3.9

FROM registry.digitalocean.com/anubis/theia-base:python-${PY_VERSION} as theia
USER root

COPY requirements.txt requirements-dev.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt -r /requirements-dev.txt

USER anubis
