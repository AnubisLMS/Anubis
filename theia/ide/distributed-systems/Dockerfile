# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.22.6

FROM node:${NODE_VERSION}-buster as theia

ENV NODE_VERSION=$NODE_VERSION
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive
ENV REPO_NAME=""

# Theia application

WORKDIR /opt/theia

COPY latest.package.json package.json
COPY motd.txt /etc/motd

ENV GO_VERSION=1.17 \
   GOOS=linux \
   GOARCH=amd64 \
   GOROOT=/opt/go
ENV PATH=$GOROOT/bin:$PATH

RUN set -ex; \
  apt update; \
  apt-get install -y --no-install-recommends \
    wget gpg apt-transport-https ca-certificates apt-utils \
    zsh git build-essential \
    gcc g++ libc6-dev \
    python3 python3-pip \
    libsecret-1-0; \
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
  chown -R anubis:anubis $GOROOT; \
  curl -fsSL https://storage.googleapis.com/golang/go$GO_VERSION.$GOOS-$GOARCH.tar.gz | tar -C $(dirname $GOROOT) -xzv; \
  cd /home/anubis; \
  echo 'export GO111MODULE=on' >> .bashrc; \
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
  go get -u -v github.com/mgechev/revive; \
  go get -u -v github.com/sourcegraph/go-langserver; \
  go get -u -v github.com/go-delve/delve/cmd/dlv; \
  go get -u -v github.com/davidrjenni/reftools/cmd/fillstruct; \
  go get -u -v -d github.com/stamblerre/gocode

COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER anubis
WORKDIR /opt/theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
