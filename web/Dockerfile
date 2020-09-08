FROM node:alpine

WORKDIR /opt/app
COPY package.json .
COPY yarn.lock .

# install dependencies
# add program for serving static
# build prod
# delete fluff
RUN apk add --update --no-cache curl && yarn \
  && yarn global add serve
COPY . .
RUN yarn run build \
  && rm -rf node_modules src public package.json yarn.lock

CMD serve -s build -l 3000
