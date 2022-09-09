FROM node:alpine

WORKDIR /opt/app
COPY . .
RUN yarn && apk add --no-cache tini
USER nobody

# Increase internal node memory limit.
# cgroup memory limit on pod will likely
# get hit first.
ENV NODE_OPTIONS="--max-old-space-size=2048"

ENTRYPOINT ["tini", "--"]
CMD ["/usr/local/bin/node", "/opt/app/index.js"]
