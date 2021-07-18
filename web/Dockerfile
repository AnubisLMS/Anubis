FROM node:alpine
WORKDIR /opt/app
COPY package.json yarn.lock /opt/app/
RUN yarn
COPY . .
RUN yarn run build \
  && rm -rf node_modules src public package.json yarn.lock \
  && find / -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'


FROM nginx:alpine
COPY --from=0 /opt/app/build /usr/share/nginx/html
