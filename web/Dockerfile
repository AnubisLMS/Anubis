FROM node:18-alpine


# This disables webpack source maps from being created in the build step
ENV GENERATE_SOURCEMAP=false DISABLE_ESLINT_PLUGIN=true

WORKDIR /opt/app
COPY package.json yarn.lock /opt/app/
RUN yarn install --frozen-lockfile

COPY . .
RUN set -eux; \
    yarn run build; \
    rm -rf node_modules src public package.json yarn.lock; \
    find /usr /home -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'


FROM node:18-alpine


WORKDIR /opt/app
RUN set -eux;  \
    apk add --no-cach tini;  \
    yarn global add serve;  \
    find / -depth -name '.cache' -exec 'rm' '-rf' '{}' ';'

COPY --from=0 /opt/app/build /opt/app/build

ARG GIT_TAG=latest
ENV GIT_TAG=${GIT_TAG}

RUN set -eux; \
    sed -i "s/GIT_TAG_PLACEHOLDER/${GIT_TAG}/" $(find /opt/app/build -type f)

USER nobody

ENTRYPOINT ["tini", "--"]
CMD ["serve", "-s", "build", "-l", "3000"]
