# https://github.com/MariaDB/mariadb-docker/blob/master/10.8/Dockerfile

ARG PY_VERSION=3.10

FROM registry.digitalocean.com/anubis/theia-base:python-${PY_VERSION} as theia
USER root

ENV MARIADB_ROOT_PASSWORD=anubis MYSQL_DATABASE=anubis MYSQL_USER=anubis MYSQL_PASSWORD=anubis

COPY supervisord.conf requirements.txt /
RUN set -eux; \
  apt update; \
  apt install -y --no-install-recommends mariadb-server mariadb-client; \
  pip3 install --no-cache-dir -r /requirements.txt; \
  rm -rf /var/lib/mysql; \
  mkdir -p /var/lib/mysql /var/run/mysqld; \
  chown -R mysql:mysql /var/lib/mysql /var/run/mysqld; \
  chmod 777 /var/run/mysqld; \
  chown anubis /var/lib/mysql; \
  find /etc/mysql/ -name '*.cnf' -print0 \
		| xargs -0 grep -lZE '^(bind-address|log|user\s)' \
		| xargs -rt -0 sed -Ei 's/^(bind-address|log|user\s)/#&/'; \
  if [ ! -L /etc/mysql/my.cnf ]; then sed -i -e '/includedir/i[mariadb]\nskip-host-cache\nskip-name-resolve\n' /etc/mysql/my.cnf; \
  else sed -i -e '/includedir/ {N;s/\(.*\)\n\(.*\)/[mariadbd]\nskip-host-cache\nskip-name-resolve\n\n\2\n\1/}' /etc/mysql/mariadb.cnf; \
  fi; \
  apt autoclean -y; \
  apt autoremove -y; \
  rm -rf /tmp/*; \
  rm -rf /usr/share/doc; \
  rm -rf /var/lib/apt/lists/*; \
  rm -rf /home/node/*; \
  find / -depth \
    \( -name .cache -o -name __pycache__ -o -name '*.pyc' -o -name .git -o -name .github \) \
    -exec 'rm' '-rf' '{}' '+'; \
  rm /requirements.txt;

COPY mysqld-entrypoint.sh supervisord.conf /
COPY motd.txt /etc/motd

USER anubis
