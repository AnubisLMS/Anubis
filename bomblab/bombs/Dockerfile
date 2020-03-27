FROM node:alpine

WORKDIR /opt/app

VOLUME /opt/app/DATA
RUN yarn global add serve

CMD serve -s /opt/app/DATA
