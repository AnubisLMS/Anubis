# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.22.6

FROM node:${NODE_VERSION}-buster as theia
ARG PY_VERSION=3.10.0

ENV PY_VERSION=$PY_VERSION
ENV NODE_VERSION=$NODE_VERSION
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive
ENV REPO_NAME=""
ENV ANUBIS=1
ENV ANUBIS_IDE=1

# Theia application

WORKDIR /opt/theia

COPY latest.package.json package.json
COPY motd.txt /etc/motd

ENV GO_VERSION=1.17 \
  GOOS=linux \
  GOARCH=amd64 \
  GOROOT=/opt/go \
  GOPATH=/opt/go-tools
ENV PATH=$GOROOT/bin:$GOPATH/bin:$PATH

RUN set -ex; \
  apt update; \
  apt-get install -y --no-install-recommends \
    wget gpg apt-transport-https ca-certificates apt-utils \
    zsh git build-essential \
    gcc g++ libc6-dev libffi-dev libexpat1-dev \
    libgdbm-dev liblzma-dev zlib1g-dev \
    libsecret-1-0; \
  apt remove -y python python-pip python3-pip python3; \
  yarn --pure-lockfile; \
  NODE_OPTIONS="--max_old_space_size=4096" yarn theia build; \
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
  pip3 install --no-cache-dir supervisor setuptools; \
  echo 'cat /etc/motd' >> /etc/skel/.bashrc; \
  cd /home/anubis; \
  chmod g+rw /home; \
  chown -R anubis:anubis /home/anubis; \
  apt reinstall libc6-dev libgcc-8-dev libgcc1 gcc-8 -y; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+'; \
  cd /home/anubis; \
  mkdir -p $GOROOT; \
  mkdir -p $GOPATH; \
  chown -R anubis:anubis $GOROOT; \
  curl -fsSL https://storage.googleapis.com/golang/go$GO_VERSION.$GOOS-$GOARCH.tar.gz | tar -C $(dirname $GOROOT) -xzv; \
  cd /home/anubis; \
  GOPROXY=direct go get -u -v github.com/uudashr/gopkgs/cmd/gopkgs; \
  go get -u -v github.com/mdempsky/gocode; \
  go get -u -v github.com/ramya-rao-a/go-outline; \
  go get -u -v github.com/acroca/go-symbols; \
  go get -u -v golang.org/x/tools/cmd/guru; \
  go get -u -v golang.org/x/tools/cmd/gorename; \
  go get -u -v github.com/fatih/gomodifytags; \
  go get -u -v github.com/haya14busa/goplay/cmd/goplay; \
  go get -u -v github.com/josharian/impl; \
  go get -u -v github.com/tylerb/gotype-live; \
  go get -u -v github.com/rogpeppe/godef; \
  go get -u -v github.com/zmb3/gogetdoc; \
  go get -u -v golang.org/x/tools/cmd/goimports; \
  go get -u -v github.com/sqs/goreturns; \
  go get -u -v winterdrache.de/goformat/goformat; \
  go get -u -v golang.org/x/lint/golint; \
  go get -u -v github.com/cweill/gotests/...; \
  go get -u -v honnef.co/go/tools/...; \
  GO111MODULE=on go get github.com/golangci/golangci-lint/cmd/golangci-lint; \
  GO111MODULE=on go get golang.org/x/tools/gopls@latest; \
  go get -u -v github.com/mgechev/revive; \
  go get -u -v github.com/sourcegraph/go-langserver; \
  go get -u -v github.com/go-delve/delve/cmd/dlv; \
  go get -u -v github.com/davidrjenni/reftools/cmd/fillstruct; \
  go get -u -v github.com/go-delve/delve/cmd/dlv; \
  go get -u -v github.com/stamblerre/gocode; \
  cp /opt/go-tools/bin/gocode /opt/go-tools/bin/gocode-gomod; \
  cp /opt/go-tools/bin/godef /opt/go-tools/bin/godef-gomod; \
  echo 'export GO111MODULE=on' >> .bashrc; \
  sed -i 's/"default": "goreturns"/"default": "goformat"/' /opt/theia/plugins/vscode-go/extension/package.json

COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER anubis
WORKDIR /opt/theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
