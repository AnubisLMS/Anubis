# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

FROM registry.digitalocean.com/anubis/theia-base:python-3.10 as theia

USER root
RUN set -ex; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    git make cmake \
    gcc-multilib g++-multilib libc6-dev \
    clangd qemu-system-i386 libgmp-dev; \
  cd /; \
  wget https://ftp.gnu.org/gnu/gdb/gdb-11.2.tar.xz; \
  tar xJf gdb-11.2.tar.xz; \
  rm gdb-11.2.tar.xz; \
  cd gdb-11.2; \
  ./configure --with-python=python3.10 --prefix=/usr/local; \
  make -j $(nproc); \
  make install; \
  cd ..; \
  rm -rf gdb-11.2; \
  echo 'set auto-load safe-path /' > /etc/anubis/skel/.gdbinit; \
  echo 'source /opt/pwndbg/gdbinit.py' >> /etc/anubis/skel/.gdbinit; \
  git clone https://github.com/pwndbg/pwndbg.git /opt/pwndbg; \
  pip3 install --no-cache-dir -r /opt/pwndbg/requirements.txt; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

USER anubis
