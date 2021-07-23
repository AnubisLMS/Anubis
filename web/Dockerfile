FROM node:alpine

WORKDIR /opt/app
COPY package.json yarn.lock /opt/app/
RUN yarn
COPY . .
RUN yarn run build \
  && rm -rf node_modules src public package.json yarn.lock \
  && find / -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'


FROM node:alpine

WORKDIR /opt/app
RUN yarn global add serve \
  && find / -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'
COPY --from=0 /opt/app/build /opt/app/build
USER nobody
CMD serve -s build -l 3000
