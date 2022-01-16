FROM registry.digitalocean.com/anubis/theia-base:python-3.10 as theia

ENV DIND_COMMIT 42b1175eda071c0e9121e1d64345928384a93df1
ENV DOCKER_LIB_COMMIT 8baa881aab85f8398d2edbbcc0da4bd1f556dd98

USER root
# https://github.com/docker-library/docker/blob/8baa881aab85f8398d2edbbcc0da4bd1f556dd98/20.10/dind/Dockerfile
RUN set -ex; \
  curl -fsSL https://download.docker.com/linux/debian/gpg \
    | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg; \
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null; \
  apt update; \
  apt install -y --no-install-recommends \
    cgroupfs-mount \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    iptables \
    e2fsprogs \
    pigz \
    pixz \
    uidmap \
    openssl \
    fuse-overlayfs; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+';

RUN set -eux; \
  addgroup --system dockremap; \
  adduser --system --ingroup dockremap dockremap; \
  echo 'dockremap:165536:65536' >> /etc/subuid; \
  echo 'dockremap:165536:65536' >> /etc/subgid; \
  wget -O /usr/local/bin/dind "https://raw.githubusercontent.com/docker/docker/${DIND_COMMIT}/hack/dind"; \
  wget -O /dind-entrypoint.sh "https://raw.githubusercontent.com/docker-library/docker/${DOCKER_LIB_COMMIT}/20.10/dind/dockerd-entrypoint.sh"; \
	chmod +x /usr/local/bin/dind /dind-entrypoint.sh; \
  usermod -aG docker anubis;

VOLUME /var/lib/docker

COPY motd.txt /etc/motd
COPY supervisord.conf /
