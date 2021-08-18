# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.18.3

FROM node:${NODE_VERSION}-buster as theia

ENV NODE_VERSION=$NODE_VERSION
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive

# Theia application

WORKDIR /opt/theia

COPY latest.package.json package.json
COPY motd.txt /etc/motd

RUN set -ex; \
  apt update; \
  apt-get install -y --no-install-recommends \
    wget gpg apt-transport-https ca-certificates apt-utils; \
  wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -; \
  echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster-12 main" \
    > /etc/apt/sources.list.d/llvm.list; \
  apt-get update; \
    apt-get install -y --no-install-recommends \
    zsh gdb git build-essential cmake \
    gcc-multilib g++-multilib \
    python3 python3-pip \
    clangd-12 \
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
  pip3 install --no-cache-dir supervisor; \
  ln -s /usr/bin/clangd-12 /usr/bin/clangd; \
  echo 'set auto-load safe-path /' > /home/anubis/.gdbinit; \
  echo 'source /opt/pwndbg/gdbinit.py' >> /home/anubis/.gdbinit; \
  git clone https://github.com/pwndbg/pwndbg.git /opt/pwndbg; \
  cd /opt/pwndbg; \
  ./setup.sh; \
  cd /home/anubis; \
  git clone https://github.com/ohmyzsh/ohmyzsh.git .oh-my-zsh; \
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
    .oh-my-zsh/custom/plugins/zsh-syntax-highlighting; \
  cp .oh-my-zsh/templates/zshrc.zsh-template .zshrc; \
  sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="gnzh"/' .zshrc; \
  sed -i 's/plugins=(git)/plugins=(git zsh-syntax-highlighting)/' .zshrc; \
  echo 'cat /etc/motd' >> .zshrc; \
  mkdir -p /opt/anubis/.theia; \
  echo '{"terminal.integrated.shell.linux": "/usr/bin/zsh"}' \
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
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name '*.a' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER anubis
WORKDIR /opt/anubis
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
