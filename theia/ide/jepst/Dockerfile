# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.18.3

FROM node:${NODE_VERSION}-buster as theia

ENV NODE_VERSION=$NODE_VERSION
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive
ENV REPO_NAME=""

# Theia application

WORKDIR /opt/theia

COPY latest.package.json package.json
COPY motd.txt /etc/motd
COPY gdbinit /home/anubis/.gdbinit

RUN set -ex; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    wget gpg apt-transport-https ca-certificates apt-utils; \
  wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -; \
  echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster-12 main" \
    > /etc/apt/sources.list.d/llvm.list; \
  apt-get update; \
    apt-get install -y --no-install-recommends \
    gdb git build-essential cmake \
    gcc-multilib g++-multilib g++ libc6-dev \
    python3 python3-pip python3-setuptools \
    clangd-12 \
    qemu-system-i386 \
    libsecret-1-0 \
    iverilog \
    nasm \
    hexedit \
    elixir \
    ; \
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
  pip3 install --no-cache-dir supervisor; \
  ln -s /usr/bin/clangd-12 /usr/bin/clangd; \
  cd /home/anubis; \
  echo 'cat /etc/motd' >> /home/anubis/.bashrc; \
  echo 'alias python=python3' >> /home/anubis/.bashrc; \
  mkdir -p /opt/anubis/.theia; \
  echo '{"terminal.integrated.shell.linux": "/bin/bash"}' \
    > /opt/anubis/.theia/settings.json; \
  chmod g+rw /home; \
  chown -R anubis:anubis /home/anubis; \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';
    


#ENV GO_VERSION=1.15 \
#    GOOS=linux \
#    GOARCH=amd64 \
#    GOROOT=/home/go \
#    GOPATH=/home/go-tools
#ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH
#
#RUN mkdir -p /home/go && \
#    mkdir -p /home/go-tools && \
#    chown -R anubis:anubis /home/go && \
#    chown -R anubis:anubis /home/go-tools;
#
#RUN curl -fsSL https://storage.googleapis.com/golang/go$GO_VERSION.$GOOS-$GOARCH.tar.gz | tar -C /home -xzv

#ENV GOPATH=/home/anubis/go
#ENV PATH=$PATH:$GOPATH/bin

#RUN cd /home/anubis; \
#    echo 'export PATH=/home/go/bin:${PATH}'  >> .bashrc; \
#    echo 'export GO111MODULE=on' >> .bashrc; \ 
#    echo 'export GOPATH=/home/anubis/go' >> .bashrc ;

COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER anubis
WORKDIR /opt/theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
