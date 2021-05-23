ARG NODE_VERSION=12.18.3

FROM node:${NODE_VERSION}
ARG version=latest
WORKDIR /home/theia
ADD $version.package.json ./package.json
RUN yarn --pure-lockfile \
  && NODE_OPTIONS="--max_old_space_size=4096" yarn theia build \
  && yarn theia download:plugins \
  && yarn --production \
  && yarn autoclean --init \
  && echo *.ts >> .yarnclean \
  && echo *.ts.map >> .yarnclean \
  && echo *.spec.* >> .yarnclean \
  && yarn autoclean --force \
  && yarn cache clean \
  && rm -rf /usr/share/doc \
  && rm -rf /home/theia/node_modules/.cache \
  && rm -rf /usr/local/share/.cache \
  && find /usr -depth \( -type d -a \( -name '.cache' \) \) -exec rm -rf '{}' + \
  && find /home -depth \( -type d -a \( -name '.cache' \) \) -exec rm -rf '{}' +


FROM node:${NODE_VERSION}
ARG PY_VERSION=3.9.3
RUN set -eux; apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates curl gnupg lsb-release cgroupfs-mount \
  && curl -fsSL https://download.docker.com/linux/debian/gpg \
    | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
  && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    make build-essential libssl-dev wget curl llvm htop zsh \
    docker-ce docker-ce-cli containerd.io; \
  rm -rf /var/lib/apt/lists/* \
  && savedAptMark="$(apt-mark showmanual)" \
  && gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)"; \
  apt-get install -y --no-install-recommends \
    gcc dpkg-dev libsqlite3-dev libncurses5-dev libbz2-dev libreadline-dev \
    xz-utils libbz2-dev libc6-dev libffi-dev libexpat1-dev \
    libgdbm-dev liblzma-dev zlib1g-dev \
  && apt-mark auto '.*' > /dev/null \
  && wget https://www.python.org/ftp/python/$PY_VERSION/Python-$PY_VERSION.tgz \
  && wget https://bootstrap.pypa.io/get-pip.py \
  && tar xvf Python-$PY_VERSION.tgz \
  && cd Python-$PY_VERSION \
  && ./configure \
    --build="$gnuArch" \
    --enable-loadable-sqlite-extensions \
    --enable-optimizations \
    --enable-option-checking=fatal \
    --enable-shared \
    --with-system-expat \
    --with-system-ffi \
    --without-ensurepip \
  && make -j $(nproc) LDFLAGS="-Wl,--strip-all" \
  && make install \
  && ldconfig \
  && cd .. \
  && rm -rf Python-$PY_VERSION \
  && rm Python-$PY_VERSION.tgz \
  && python3 get-pip.py \
    --disable-pip-version-check \
    --no-cache-dir \
  && rm get-pip.py; \
  pip3 install --upgrade --no-cache-dir pip \
  && pip3 install --upgrade --no-cache-dir python-language-server flake8 autopep8 pylint supervisor \
  && adduser --disabled-password --gecos '' --uid 1001 theia; \
  cd /home/theia; \
  git clone https://github.com/ohmyzsh/ohmyzsh.git .oh-my-zsh; \
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
    .oh-my-zsh/custom/plugins/zsh-syntax-highlighting; \
  cp .oh-my-zsh/templates/zshrc.zsh-template .zshrc; \
  sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="gnzh"/' .zshrc; \
  sed -i 's/plugins=(git)/plugins=(git zsh-syntax-highlighting)/' .zshrc; \
  mkdir -p /home/theia/.theia; \
  echo '{"terminal.integrated.shell.linux": "/usr/bin/zsh"}' \
    > /home/theia/.theia/settings.json; \
  rm -rf /tmp/* \
  && rm -rf /usr/share/doc \
  && rm -rf /root/.cache \
  && rm -rf /home/theia/node_modules/.cache \
  && mkdir -p /home/project \
  && chmod g+rw /home \
  && mkdir -p /home/project \
  && chown -R theia:theia /home/theia \
  && chown -R theia:theia /home/project \
  && usermod -aG docker theia \
  && find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec rm -rf '{}' + \
  && apt-mark manual $savedAptMark \
  && find /usr/local -type f -executable -not \( -name '*tkinter*' \) -exec ldd '{}' ';' \
  | awk '/=>/ { print $(NF-1) }' \
  | sort -u \
  | xargs -r dpkg-query --search \
  | cut -d: -f1 \
  | sort -u \
  | xargs -r apt-mark manual \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/cache/apt/* \
  && rm -rf /var/lib/apt/lists/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name *.pyc -o -name *.a -o -name .git -o -name .github \) \
    -exec rm -rf {} +
COPY --from=0 /home/theia /home/theia

COPY cli /cli
RUN pip3 install --no-cache-dir /cli \
  && rm -rf /cli \
  && find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test -o -name __pycache__ \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec rm -rf '{}' +
COPY supervisord.conf initialize-incluster.py autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
