FROM registry.digitalocean.com/anubis/theia-base:python-3.9-bare as theia
USER root

# Copy file over for skel initialization
COPY gdbinit /etc/anubis/skel/.gdbinit
COPY motd.txt /etc/motd

# Step for downloading any new extensions
COPY latest.package.json package.json
RUN set -ex; \
  yarn --pure-lockfile; \
  yarn theia download:plugins; \
  yarn --production; \
  yarn autoclean --force; \
  yarn cache clean; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

# Install extra tools
RUN set -ex; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    gdb \
    ghc \
    swi-prolog \
    iverilog \
    nasm \
    hexedit \
    yosys \
    unzip \
    elixir; \
  wget https://github.com/haskell/haskell-language-server/releases/download/1.5.1/haskell-language-server-Linux-9.0.1.gz; \
  gzip -d haskell-language-server-Linux-9.0.1.gz; \
  chmod +x haskell-language-server-Linux-9.0.1; \
  mv haskell-language-server-Linux-9.0.1 /usr/local/bin/haskell-language-server; \
  rm -rf /var/lib/apt/lists/*;

# Compile and install glibc 2.32 from source
RUN set -ex; \
  cd /; \
  wget https://snapshot.debian.org/archive/debian/20211205T084953Z/pool/main/g/glibc/libc6_2.32-4_amd64.deb; \
  wget https://snapshot.debian.org/archive/debian/20211205T084953Z/pool/main/g/glibc/locales_2.32-4_all.deb; \
  wget https://snapshot.debian.org/archive/debian/20211205T084953Z/pool/main/g/glibc/libc-bin_2.32-4_amd64.deb; \
  wget https://snapshot.debian.org/archive/debian/20211205T084953Z/pool/main/g/glibc/libc-l10n_2.32-4_all.deb; \
  dpkg --install libc-l10n_2.32-4_all.deb libc-bin_2.32-4_amd64.deb locales_2.32-4_all.deb libc6_2.32-4_amd64.deb; \
  rm *.deb; \
  ldconfig

USER anubis
