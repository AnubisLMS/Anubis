FROM node:alpine

WORKDIR /opt/app
COPY . .
RUN yarn

USER nobody
ENTRYPOINT ["/usr/local/bin/node"]
CMD ["/opt/app/index.js"]
