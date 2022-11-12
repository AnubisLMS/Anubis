FROM python:3.10-alpine

RUN set -eux; \
    adduser -D -u 1001 -h /home/theia anubis; \
    apk add --update --no-cache git bash; \
    pip3 install --no-cache-dir flask supervisor gunicorn

USER anubis
RUN set -eux; \
    git config --global user.email anubis@anubis-lms.io; \
    git config --global user.name anubis-robot; \
    git config --global credential.store helper; \
    git config --global credential.helper 'store --file ~/.git-credentials'; \
    git config --global core.hooksPath /dev/null
USER root

VOLUME /home/anubis

COPY supervisord.conf /supervisord.conf
COPY autograde /opt/app/autograde

USER anubis
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]


