FROM python:3.8-alpine

ENV SECRET_KEY=DEFAULT

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN apk add --update --no-cache mariadb-client git curl tzdata gcc musl-dev \
  && pip3 install -r ./requirements.txt \
  && adduser -D anubis \
  && chown anubis:anubis -R /opt/app \
  && ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime

USER anubis

COPY . .

CMD ./docker-entrypoint.sh
