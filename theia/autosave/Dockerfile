FROM python:3.10-alpine

RUN adduser -D -u 1001 -h /home/theia anubis \
  && apk add --update --no-cache git bash \
  && pip3 install --no-cache-dir flask supervisor gunicorn

USER anubis
RUN git config --global user.email anubis@anubis-lms.io \
  && git config --global user.name anubis-robot \
  && git config --global credential.store helper \
  && git config --global credential.helper 'store --file ~/.git-credentials' \
  && git config --global core.hooksPath /dev/null
USER root

VOLUME /home/project
VOLUME /log

COPY supervisord.conf /supervisord.conf
COPY autosave-loop.sh /autosave-loop.sh
COPY autosave.sh /autosave.sh
COPY app.py /app.py

USER anubis
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]


