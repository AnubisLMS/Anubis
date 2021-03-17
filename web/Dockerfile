FROM node:alpine
WORKDIR /opt/app
COPY package.json .
COPY yarn.lock .
RUN yarn
COPY . .
RUN yarn run build \
  && rm -rf node_modules src public package.json yarn.lock


FROM node:alpine
WORKDIR /opt/app
RUN apk add --update --no-cache curl && yarn global add serve
COPY --from=0 /opt/app/build /opt/app/build


CMD serve -s build -l 3000
