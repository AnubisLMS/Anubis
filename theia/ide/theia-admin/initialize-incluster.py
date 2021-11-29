#!/usr/bin/env python3

import os
import json
import base64

incluster = os.environ.get('INCLUSTER', None)
course_context = os.environ.get('COURSE_CONTEXT', None)

if incluster is None:
    print('CANNOT SEE INCLUSTER ENV')
    exit(1)

os.makedirs('/home/anubis/.anubis/', exist_ok=True)
json.dump({
    "incluster": base64.b64decode(incluster.encode()).decode(),
    'course_context': course_context,
}, open('/home/anubis/.anubis/config.json', 'w'))

