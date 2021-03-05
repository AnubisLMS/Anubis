FROM python:3-alpine

RUN adduser -D -u 1001 theia \
  && apk add --update --no-cache dcron git busybox-suid \
  && pip3 install --no-cache-dir flask supervisor gunicorn

VOLUME /home/project

COPY supervisord.conf /supervisord.conf
COPY autosave-loop.sh /autosave-loop.sh
COPY autosave.sh /autosave.sh
COPY app.py /app.py

ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]


