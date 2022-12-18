FROM node:16-alpine


# This disables webpack source maps from being created in the build step
ENV GENERATE_SOURCEMAP=false

WORKDIR /opt/app
COPY package.json yarn.lock /opt/app/
RUN yarn install --frozen-lockfile

ARG REACT_APP_GIT_TAG=latest
ENV REACT_APP_GIT_TAG=${REACT_APP_GIT_TAG}

COPY . .
RUN set -eux; \
    yarn run build; \
    rm -rf node_modules src public package.json yarn.lock; \
    find /usr /home -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'


FROM node:16-alpine

WORKDIR /opt/app
RUN set -eux;  \
    apk add --no-cach tini;  \
    yarn global add serve;  \
    find / -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'
COPY --from=0 /opt/app/build /opt/app/build
USER nobody

ENTRYPOINT ["tini", "--"]
CMD ["serve", "-s", "build", "-l", "3000"]
