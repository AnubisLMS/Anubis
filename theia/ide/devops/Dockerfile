# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.18.3

FROM node:${NODE_VERSION} as build
ARG version=latest
WORKDIR /opt/theia
ADD $version.package.json ./package.json
RUN set -ex; \
  apt-get update; \
  apt-get install -y --no-install-recommends libsecret-1-0; \
  yarn --pure-lockfile; \
  NODE_OPTIONS="--max_old_space_size=4096" yarn theia build; \
  yarn theia download:plugins; \
  yarn --production; \
  yarn autoclean --init; \
  echo *.ts >> .yarnclean; \
  echo *.ts.map >> .yarnclean; \
  echo *.spec.* >> .yarnclean; \
  yarn autoclean --force; \
  yarn cache clean; \
  rm -rf /usr/share/doc; \
  rm -rf /opt/theia/node_modules/.cache; \
  rm -rf /usr/local/share/.cache; \
  find /usr -depth \( -type d -a \( -name '.cache' \) \) -exec rm -rf '{}' +; \
  find /home -depth \( -type d -a \( -name '.cache' \) \) -exec rm -rf '{}' +; \
  apt autoremove -y; \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*

ARG NODE_VERSION=12.18.3

##################################################################################

FROM node:${NODE_VERSION} as theia
ARG PY_VERSION=3.9.6

COPY --from=0 /opt/theia /opt/theia
COPY requirements.txt requirements-dev.txt /

RUN set -eux; apt-get update; \
  apt-get upgrade -y --no-install-recommends; \
  apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates gnupg lsb-release; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    make build-essential libssl-dev wget curl htop \
    libsecret-1-0; \
  apt remove python python3 -y; \
  rm -rf /var/lib/apt/lists/*; \
  savedAptMark="$(apt-mark showmanual)"; \
  gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)"; \
  apt-get install -y --no-install-recommends \
    gcc dpkg-dev libsqlite3-dev libncurses5-dev libbz2-dev libreadline-dev \
    xz-utils libbz2-dev libc6-dev libffi-dev libexpat1-dev \
    libgdbm-dev liblzma-dev zlib1g-dev; \
  apt-mark auto '.*' > /dev/null; \
  wget https://www.python.org/ftp/python/$PY_VERSION/Python-$PY_VERSION.tgz; \
  wget https://bootstrap.pypa.io/get-pip.py; \
  tar xvf Python-$PY_VERSION.tgz; \
  cd Python-$PY_VERSION; \
  ./configure \
    --build="$gnuArch" \
    --enable-loadable-sqlite-extensions \
    --enable-optimizations \
    --enable-option-checking=fatal \
    --enable-shared \
    --with-system-expat \
    --with-system-ffi \
    --without-ensurepip; \
  make -j $(nproc) LDFLAGS="-Wl,--strip-all"; \
  make install; \
  ldconfig; \
  cd ..; \
  rm -rf Python-$PY_VERSION; \
  rm Python-$PY_VERSION.tgz; \
  python3 get-pip.py \
    --disable-pip-version-check \
    --no-cache-dir; \
  rm get-pip.py; \
  pip3 install --upgrade --no-cache-dir pip; \
  pip3 install --upgrade --no-cache-dir python-language-server flake8 autopep8 pylint supervisor; \
  pip3 install --no-cache-dir -r /requirements.txt -r /requirements-dev.txt; \
  adduser --disabled-password --gecos '' --uid 1001 anubis; \
  cd /home/anubis; \
  echo 'cat /etc/motd' >> /etc/skel/.bashrc; \
  rm -rf /tmp/* \
  rm -rf /usr/share/doc; \
  rm -rf /root/.cache; \
  chmod g+rw /home; \
  chown -R anubis:anubis /home/anubis; \
  find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec rm -rf '{}' +; \
  apt-mark manual $savedAptMark; \
  find /usr/local -type f -executable -not \( -name '*tkinter*' \) -exec ldd '{}' ';' \
  | awk '/=>/ { print $(NF-1) }' \
  | sort -u \
  | xargs -r dpkg-query --search \
  | cut -d: -f1 \
  | sort -u \
  | xargs -r apt-mark manual; \
  apt autoremove -y; \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name *.pyc -o -name *.a -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+'; \
  rm -rf /home/node; \
  find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test -o -name __pycache__ \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec 'rm' '-rf' '{}' '+'

COPY motd.txt /etc/motd
COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER anubis
WORKDIR /opt/theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
