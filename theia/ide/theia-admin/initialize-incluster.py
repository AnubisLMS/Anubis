#!/usr/bin/env python3

import os
import json
import base64

incluster = os.environ.get('INCLUSTER', None)

if incluster is None:
    print('CANNOT SEE INCLUSTER ENV')
    exit(1)

incluster = base64.b64decode(incluster.encode()).decode()

os.makedirs('/home/anubis/.anubis/', exist_ok=True)
json.dump({
    "incluster": incluster
}, open('/home/anubis/.anubis/config.json', 'w'))

