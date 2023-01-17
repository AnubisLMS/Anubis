FROM python:3.10-slim-bullseye

ENV DEBUG=0
ENV MINDEBUG=0
ENV MAX_CONCURRENCY=8
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV HOME=/home/anubis

WORKDIR /opt/app

COPY requirements/common.txt requirements.txt

RUN set -eux;  \
    apt update; \
    apt install -y make mariadb-client git tzdata gcc g++ libmagic-dev fonts-roboto; \
    pip3 install --no-cache-dir -r ./requirements.txt; \
    useradd -M anubis; \
    chown anubis:anubis -R /opt/app; \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime; \
    apt purge -y gcc g++; \
    apt autoremove -y; \
    env USER=root find /opt/app -depth \
    \( \
    \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
    -o \( -type f -a \( -name "*.pyc" -o -name "*.pyo" -o -name "*.a" \) \) \
    \) -exec rm -rf "{}" + ; \
    \
    env USER=root find /usr/local -depth \
    \( \
    \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
    -o \( -type f -a \( -name "*.pyc" -o -name "*.pyo" -o -name "*.a" \) \) \
    \) -exec rm -rf "{}" + ; \
    rm -rf /usr/share/doc; \
    rm -rf /usr/lib/gcc; \
    rm -rf /usr/local/share/.cache; \
    rm -rf /var/cache/apt/*; \
    rm -rf /var/lib/apt/lists/*

USER anubis

COPY . .

ARG GIT_TAG=latest
ENV GIT_TAG=${GIT_TAG}

USER nobody
CMD python3 -m gunicorn -b 0.0.0.0:5000 anubis.app:create_app()
