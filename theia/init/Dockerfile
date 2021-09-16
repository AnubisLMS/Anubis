FROM debian:buster-slim

# Create out directory
VOLUME /out

# Only dependency is git
RUN set -ex; \
  apt update; \
  apt install --no-install-recommends -y ca-certificates git bash; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*; \
  echo 'set auto-load safe-path /' > /etc/skel/.gdbinit; \
  echo 'source /opt/pwndbg/gdbinit.py' >> /etc/skel/.gdbinit;

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh

# Set entrypoint
CMD /entrypoint.sh

