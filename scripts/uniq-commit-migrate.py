#!/usr/bin/python3


# docker run -it -v $(dirname $(pwd)):/root/host --net traefik-proxy -w /root/host/scripts python:3.8-alpine sh -c 'pip3 install -r ../api/requirements.txt && python3 uniq-commit-migrate.py'
# docker-compose exec -T db mysql -u root --password=password os <<< 'alter table submissions add unique(commit);'

import sys

sys.path.append('../api/')

from src import db
from src.models import Submissions
from sqlalchemy import desc



submissions = Submissions.query.order_by(Submissions.id.desc()).all()

f = set()

for s in submissions:
    if s.commit in f:
        db.session.delete(s)
    else:
        f.add(s.commit)

db.session.commit()
