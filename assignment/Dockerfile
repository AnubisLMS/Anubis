FROM ubuntu:16.04

RUN apt update \
  && apt install -y git python3 python3-pip \
  && pip3 install pyyaml requests gitpython
RUN useradd --create-home -u 1000 anubis \
  && useradd --no-create-home -u 1001 student \
  && usermod -aG student anubis \
  && chmod 700 /home/anubis \
  && sed -i 's/pam_rootok.so/pam_rootok.so\nauth  sufficient                 pam_succeed_if.so use_uid user = anubis/' /etc/pam.d/su \
  && sed -i 's/pam_rootok.so/pam_rootok.so\nauth  [success=ignore default=1] pam_succeed_if.so user = student/' /etc/pam.d/su \
  && mkdir /home/anubis/student \
  && chown anubis:student /home/anubis/student \
  && chmod g+w /home/anubis/student
WORKDIR /home/anubis
USER anubis

COPY assignment.py assignment.py

CMD assignment.py
