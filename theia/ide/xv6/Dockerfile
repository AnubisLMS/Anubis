# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

ARG NODE_VERSION=12.18.3

FROM node:${NODE_VERSION}-buster as theia

ENV NODE_VERSION=$NODE_VERSION
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive

# Theia application

WORKDIR /home/theia

COPY latest.package.json package.json
COPY motd.txt /etc/motd

RUN set -ex; \
  chown -R 1001:1001 /home/theia; \
  cp /etc/skel/.bash_logout /etc/skel/.bashrc /etc/skel/.profile /home/theia/; \
  adduser --disabled-password --gecos '' --uid 1001 theia; \
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
    qemu-system-i386; \
  pip3 install --no-cache-dir supervisor; \
  ln -s /usr/bin/clangd-12 /usr/bin/clangd; \
  echo 'set auto-load safe-path /' > /home/theia/.gdbinit \
  && echo 'source /opt/pwndbg/gdbinit.py' >> /home/theia/.gdbinit \
  && git clone https://github.com/pwndbg/pwndbg.git /opt/pwndbg \
  && cd /opt/pwndbg \
  && ./setup.sh; \
  cd /home/theia; \
  git clone https://github.com/ohmyzsh/ohmyzsh.git .oh-my-zsh; \
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
    .oh-my-zsh/custom/plugins/zsh-syntax-highlighting; \
  cp .oh-my-zsh/templates/zshrc.zsh-template .zshrc; \
  sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="gnzh"/' .zshrc; \
  sed -i 's/plugins=(git)/plugins=(git zsh-syntax-highlighting)/' .zshrc; \
  echo 'cat /etc/motd' >> .zshrc; \
  mkdir -p /home/theia/.theia; \
  echo '{"terminal.integrated.shell.linux": "/usr/bin/zsh"}' \
    > /home/theia/.theia/settings.json; \
  chmod g+rw /home \
  && mkdir -p /home/project \
  && chown -R theia:theia /home/theia \
  && chown -R theia:theia /home/project; \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name '*.a' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

COPY supervisord.conf autosave-dump.sh /
COPY autosave /usr/local/bin/autosave

USER theia
ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
