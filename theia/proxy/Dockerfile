FROM node:18-alpine

WORKDIR /opt/app
COPY . .
RUN set -eux; \
    apk add --no-cache tini tzdata; \
    ln -s /usr/share/zoneinfo/America/New_York /etc/localtime; \
    yarn --production;
USER nobody

# Increase internal node memory limit.
# cgroup memory limit on pod will likely
# get hit first.
ENV NODE_OPTIONS="--max-old-space-size=2048"

ENTRYPOINT ["tini", "--"]
CMD ["/usr/local/bin/node", "/opt/app/index.js"]
