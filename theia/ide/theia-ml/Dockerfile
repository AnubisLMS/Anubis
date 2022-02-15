ARG PY_VERSION=3.9

FROM registry.digitalocean.com/anubis/theia-base:python-${PY_VERSION} as theia
USER root

# Step for downloading any new extensions
COPY latest.package.json package.json
RUN set -ex; \
  yarn --pure-lockfile; \
  yarn theia download:plugins; \
  yarn --production; \
  yarn autoclean --force; \
  yarn cache clean; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

COPY requirements.txt requirements-dev.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt -r /requirements-dev.txt

USER anubis
