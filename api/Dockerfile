FROM python:3.8-alpine

ENV SECRET_KEY=DEFAULT

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN apk add --update --no-cache mariadb-client git tzdata gcc g++ musl-dev libmagic \
  && pip3 install --no-cache-dir -r ./requirements.txt \
  && adduser -D anubis \
  && chown anubis:anubis -R /opt/app \
  && ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \
  && apk del gcc g++ \
  && env USER=root find /opt/app -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec rm -rf '{}' + \
  \
  && env USER=root find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec rm -rf '{}' +


USER anubis

COPY . .

CMD ./docker-entrypoint.sh
