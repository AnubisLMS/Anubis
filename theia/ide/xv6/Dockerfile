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

RUN set -ex; \
  apt update; \
  apt-get install -y --no-install-recommends \
    wget gpg apt-transport-https ca-certificates apt-utils; \
  wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -; \
  echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster main" \
    > /etc/apt/sources.list.d/llvm.list; \
  apt-get update; \
    apt-get install -y --no-install-recommends \
    zsh gdb git build-essential cmake \
    gcc-multilib g++-multilib libc6-dev \
    python3 python3-pip \
    clangd \
    qemu-system-i386 \
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
  echo 'set auto-load safe-path /' > /etc/skel/.gdbinit; \
  echo 'source /opt/pwndbg/gdbinit.py' >> /etc/skel/.gdbinit; \
  git clone https://github.com/pwndbg/pwndbg.git /opt/pwndbg; \
  cd /opt/pwndbg; \
  ./setup.sh; \
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
    -exec 'rm' '-rf' '{}' '+';

COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER anubis
WORKDIR /opt/theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
