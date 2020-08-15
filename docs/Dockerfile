FROM registry.osiris.services/anubis/api:latest

USER root
RUN pip3 install docutils
COPY . /opt/doc
COPY conf.py .

RUN /opt/doc/m.css/documentation/python.py conf.py


FROM nginx

COPY --from=0 /opt/app/output /usr/share/nginx/html
