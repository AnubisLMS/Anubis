FROM node:alpine

# This disables webpack source maps from being created in the build step
ENV GENERATE_SOURCEMAP=false

WORKDIR /opt/app
COPY package.json yarn.lock /opt/app/
RUN yarn install --frozen-lockfile
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
