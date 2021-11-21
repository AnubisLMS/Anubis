FROM registry.digitalocean.com/anubis/theia-base:python-3.10.0 as theia

ENV DIND_COMMIT 42b1175eda071c0e9121e1d64345928384a93df1
ENV DOCKER_LIB_COMMIT 8baa881aab85f8398d2edbbcc0da4bd1f556dd98

USER root
# https://github.com/docker-library/docker/blob/8baa881aab85f8398d2edbbcc0da4bd1f556dd98/20.10/dind/Dockerfile
RUN set -ex; \
  apt update; \
  apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates curl gnupg lsb-release cgroupfs-mount; \
  curl -fsSL https://download.docker.com/linux/debian/gpg \
    | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg; \
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null; \
  apt update; \
  apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    iptables \
    aufs-tools \
    btrfs-progs \
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

COPY cli /cli
RUN pip3 install --no-cache-dir /cli \
  && rm -rf /cli \
  && rm -rf /home/node \
  && find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test -o -name __pycache__ \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec 'rm' '-rf' '{}' '+'

COPY motd.txt /etc/motd
COPY supervisord.conf initialize-incluster.py /
