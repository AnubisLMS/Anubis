FROM debian:trixie-slim

# Create out directory
VOLUME /home/anubis/

# Only dependency is git
RUN set -ex; \
  apt update; \
  apt install --no-install-recommends -y ca-certificates git bash; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*;

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh

# Set entrypoint
CMD /entrypoint.sh

