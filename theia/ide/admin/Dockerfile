ARG NODE_VERSION=12.18.3

FROM node:${NODE_VERSION}
ARG version=latest
WORKDIR /home/theia
ADD $version.package.json ./package.json
RUN yarn --pure-lockfile \
  && NODE_OPTIONS="--max_old_space_size=4096" yarn theia build \
  && yarn theia download:plugins \
  && yarn --production \
  && yarn autoclean --init \
  && echo *.ts >> .yarnclean \
  && echo *.ts.map >> .yarnclean \
  && echo *.spec.* >> .yarnclean \
  && yarn autoclean --force \
  && yarn cache clean \
  && rm -rf /usr/share/doc \
  && rm -rf /home/theia/node_modules/.cache \
  && rm -rf /usr/local/share/.cache

FROM node:${NODE_VERSION}


# PYTHON Version
ARG PY_VERSION=3.9.1
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y make build-essential libssl-dev \
  && apt-get install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm htop \
  && apt-get install -y libncurses5-dev  libncursesw5-dev xz-utils tk-dev \
  && curl "https://get.docker.com/" | sh \
  && wget https://www.python.org/ftp/python/$PY_VERSION/Python-$PY_VERSION.tgz \
  && wget https://bootstrap.pypa.io/get-pip.py \
  && tar xvf Python-$PY_VERSION.tgz \
  && cd Python-$PY_VERSION \
  && ./configure \
  && make -j $(nproc) \
  && make install \
  && cd .. \
  && rm -rf Python-$PY_VERSION \
  && rm Python-$PY_VERSION.tgz \
  && python3 get-pip.py \
  && rm get-pip.py \
  && pip3 install --upgrade --no-cache-dir pip \
  && pip3 install --upgrade --no-cache-dir python-language-server flake8 autopep8 pylint supervisor \
  && apt-get clean \
  && apt-get auto-remove -y \
  && rm -rf /var/cache/apt/* \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /tmp/* \
  && rm -rf /usr/share/doc \
  && rm -rf /root/.cache \
  && rm -rf /home/theia/node_modules/.cache \
  && adduser --disabled-password --gecos '' --uid 1001 theia \
  && mkdir -p /home/project \
  && chmod g+rw /home \
  && mkdir -p /home/project \
  && chown -R theia:theia /home/theia \
  && chown -R theia:theia /home/project \
  && usermod -aG docker theia

COPY --from=0 /home/theia /home/theia

COPY cli /cli
COPY supervisord.conf /supervisord.conf
RUN pip3 install /cli

ENTRYPOINT ["supervisord", "--nodaemon", "-c", "/supervisord.conf"]
