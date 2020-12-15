FROM alpine:latest

RUN adduser -D -u 1001 theia \
  && apk add --update --no-cache fcron git busybox-suid \
  && chmod +x /usr/sbin/fcron

VOLUME /home/project

COPY entrypoint.sh /entrypoint.sh
COPY autosave.sh /autosave.sh

CMD /entrypoint.sh


