FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN set -ex; \
  apt update; \
  apt install -y apt-utils; \
  apt install -y  --no-install-recommends \
    gcc-multilib libc6-dev build-essential \
    git python3 python3-pip qemu-system-x86; \
  apt reinstall libc6-dev libgcc-8-dev libgcc1 gcc-8 -y; \
  pip3 install --no-cache-dir setuptools ; \
  pip3 install --no-cache-dir pyyaml requests gitpython parse lorem; \
  apt autoremove -y; \
  find / -name .cache -exec 'rm' '-rf' '{}' ';'; \
  rm -rf /var/cache/apt/*; \
  rm -rf /var/lib/apt/lists/*; \
  useradd --create-home --user-group -u 1000 anubis; \
  useradd --no-create-home --user-group -u 1001 student; \
  usermod -aG student anubis; \
  mkdir -p /anubis; \
  chown anubis:anubis /anubis; \
  chmod 700 /anubis; \
  chmod 700 /home/anubis; \
  mkdir -p /anubis/student; \
  chown student:student /anubis/student; \
  chmod 770 /anubis/student; \
  sed -i 's/# auth       sufficient pam_wheel.so trust/auth       sufficient pam_wheel.so trust group=anubis/' /etc/pam.d/su

ENV PATH=/bin:/sbin:/usr/bin:/usr/local/bin:/usr/lib/gcc/x86_64-linux-gnu/8
ENV HOME=/home/anubis
USER anubis
WORKDIR /anubis
COPY pipeline.py utils.py meta.yml assignment.py /anubis/

CMD python3 pipeline.py
