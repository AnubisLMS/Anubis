FROM python:3.9-slim-buster

ENV SECRET_KEY=DEFAULT
ENV DEBUG=0
ENV MINDEBUG=0

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN apt update \
  && apt install -y mariadb-client git tzdata gcc g++ libmagic-dev \
  && pip3 install --no-cache-dir -r ./requirements.txt \
  && useradd -M anubis \
  && chown anubis:anubis -R /opt/app \
  && ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \
  && apt purge -y gcc g++ \
  && apt autoremove -y \
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
  \) -exec rm -rf '{}' + \
  && rm -rf /usr/share/doc \
  && rm -rf /usr/lib/gcc \
  && rm -rf /usr/local/share/.cache \
  && rm -rf /var/cache/apt/* \
  && rm -rf /var/lib/apt/lists/*

USER anubis

COPY . .

USER nobody
CMD ./docker-entrypoint.sh
