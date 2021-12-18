FROM registry.digitalocean.com/anubis/theia-base:python-3.9 as theia

COPY gdbinit /etc/skel/.gdbinit

USER root
RUN set -ex; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    ghc \
    swi-prolog \
    iverilog \
    nasm \
    hexedit \
    elixir; \
  rm -rf /var/lib/apt/lists/*;
USER anubis