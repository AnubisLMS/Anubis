FROM python:3.8-alpine

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN apk add --update --no-cache make mariadb-client git \
  && pip3 install -r ./requirements.txt \
  && adduser -HD os3224 \
  && chown os3224:os3224 -R /opt/app \
  && ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

USER os3224

COPY . .

CMD make deploy
