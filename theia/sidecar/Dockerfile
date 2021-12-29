FROM python:3.10-alpine

RUN adduser -D -u 1001 theia \
  && apk add --update --no-cache git bash \
  && pip3 install --no-cache-dir flask supervisor gunicorn

USER theia
RUN git config --global user.email noreply@anubis.osiris.services \
  && git config --global user.name os3224-robot \
  && git config --global credential.store helper \
  && git config --global credential.helper 'store --file ~/.git-credentials'
USER root

VOLUME /home/project

COPY supervisord.conf /supervisord.conf
COPY autosave-loop.sh /autosave-loop.sh
COPY autosave.sh /autosave.sh
COPY app.py /app.py

USER theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]


