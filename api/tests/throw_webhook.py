#!/usr/bin/env python3

import sys
import json
import requests


data = json.loads(open('./webhook1.json').read())

r = requests.post(
    #'https://anubis.osiris.services/api/public/webhook',
    'http://localhost:5000/public/webhook',
    headers={'Content-Type': 'application/json', 'X-GitHub-Event': 'push'},
    json=data,
)

print(r.status_code)
print(r.text)

