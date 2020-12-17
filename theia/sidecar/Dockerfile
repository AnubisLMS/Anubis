FROM alpine:latest

RUN adduser -D -u 1001 theia \
  && apk add --update --no-cache dcron git busybox-suid

VOLUME /home/project

COPY entrypoint.sh /entrypoint.sh
COPY autosave.sh /autosave.sh

USER theia
ENTRYPOINT /entrypoint.sh


