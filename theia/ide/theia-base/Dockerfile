# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.22.6

FROM node:${NODE_VERSION}-bullseye-slim as base

ARG PY_VERSION=3.10.0
ENV PY_VERSION=$PY_VERSION \
    NODE_VERSION=$NODE_VERSION \
    TERM=xterm-256color \
    DEBIAN_FRONTEND=noninteractive \
    REPO_NAME="" \
    ANUBIS=1 \
    ANUBIS_IDE=1

WORKDIR /opt/theia

# Setup high level dependencies (mainly python)
RUN set -ex; \
  apt update; \
  apt upgrade -y; \
  apt-get install -y --no-install-recommends \
    wget gpg gnupg apt-transport-https ca-certificates apt-utils; \
  wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -; \
  echo "deb http://apt.llvm.org/bullseye/ llvm-toolchain-bullseye main" \
    > /etc/apt/sources.list.d/llvm.list; \
  apt-get update; \
    apt-get install -y --no-install-recommends \
    git curl wget build-essential tree clangd zsh exa \
    libffi-dev libexpat1-dev \
    libgdbm-dev liblzma-dev zlib1g-dev \
    libsqlite3-dev libssl-dev openssl \
    libsecret-1-0 sqlite3 bzip2; \
  apt remove -y python python-pip python3-pip python3; \
  cd /; \
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
  ln -sf /usr/local/bin/python3 /usr/local/bin/python; \
  ln -sf /usr/local/bin/python3 /usr/bin/python3; \
  ln -sf /usr/local/bin/python3 /usr/bin/python; \
  cd ..; \
  rm -rf Python-$PY_VERSION; \
  rm Python-$PY_VERSION.tgz; \
  python3 get-pip.py \
    --disable-pip-version-check \
    --no-cache-dir; \
  rm get-pip.py; \
  pip3 install --upgrade --no-cache-dir pip; \
  pip3 install --upgrade --no-cache-dir python-language-server supervisor setuptools; \
  adduser --disabled-password --gecos '' --uid 1001 anubis; \
  chown -R 1001:1001 /home/anubis; \
  cd /home/anubis; \
  cp /etc/skel/.bash_logout /etc/skel/.bashrc /etc/skel/.profile /home/anubis/; \
  echo 'cat /etc/motd' >> /etc/skel/.bashrc; \
  cd /home/anubis; \
  chmod g+rw /home; \
  chown -R anubis:anubis /home/anubis; \
  apt remove -y libffi-dev libexpat1-dev \
    libgdbm-dev liblzma-dev zlib1g-dev; \
  apt autoclean -y; \
  apt autoremove -y; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

# Build Theia Application
COPY latest.package.json package.json
RUN set -ex; \
  yarn --pure-lockfile; \
  NODE_OPTIONS="--max-old-space-size=4096" yarn theia build; \
  HEAD_LINE_NUMBER=$(grep -n '</head>' lib/index.html | cut -f1 -d:); \
  SCRIPT_LINE='<script>function ping(){if (document.hasFocus()){fetch("/ide/ping")}};document.addEventListener("focus",ping);setInterval(ping,60000)</script>'; \
  sed -i "${HEAD_LINE_NUMBER}i${SCRIPT_LINE}" lib/index.html; \
  yarn theia download:plugins; \
  yarn --production; \
  yarn autoclean --init; \
  echo *.ts >> .yarnclean; \
  echo *.ts.map >> .yarnclean; \
  echo *.spec.* >> .yarnclean; \
  yarn autoclean --force; \
  yarn cache clean; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

# PRETTY SHELL NECESSARY
RUN set -ex; \
  chsh -s /usr/bin/zsh anubis; \
  git clone https://github.com/robbyrussell/oh-my-zsh.git /opt/.oh-my-zsh; \
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git /opt/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting;
COPY zshrc /etc/skel/.zshrc

# Anubis CLI
COPY cli /cli
RUN pip3 install --no-cache-dir /cli \
  && rm -rf /cli

COPY motd.txt /etc/motd
COPY supervisord.conf initialize-ide.py /

USER anubis
WORKDIR /opt/theia
ENTRYPOINT ["/usr/local/bin/supervisord", "--nodaemon", "-c", "/supervisord.conf"]
