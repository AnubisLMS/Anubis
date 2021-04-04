#!/usr/bin/env python3

import os
import sys
import json
import base64

incluster = os.environ.get('INCLUSTER', None)

if incluster is None:
    print('CANNOT SEE INCLUSTER ENV', file=sys.stderr)
    exit(1)

incluster = base64.b64decode(incluster.encode()).decode()

os.makedirs('/home/theia/.anubis/', exist_ok=True)
json.dump({
    "auth": {"username": None, "password": None},
    "incluster": incluster
}, open('/home/theia/.anubis/config.json', 'w'))

