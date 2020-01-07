FROM python:3.8-alpine

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN apk add --update --no-cache make mariadb-client \
  && pip3 install -r ./requirements.txt \
  && adduser -HD os3224 \
  && chown os3224:os3224 -R /opt/app

USER os3224

COPY . .

CMD gunicorn -b 0.0.0.0:5000 -w 8 app:app
