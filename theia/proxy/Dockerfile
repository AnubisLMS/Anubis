FROM node:alpine

WORKDIR /opt/app
COPY . .
RUN yarn
USER nobody

# Increase internal node memory limit.
# cgroup memory limit on pod will likely
# get hit first.
ENV NODE_OPTIONS="--max-old-space-size=2048"

ENTRYPOINT ["/usr/local/bin/node"]
CMD ["/opt/app/index.js"]
