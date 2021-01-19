import json

import requests

from utils import app_context
from anubis.models import Assignment
import os
import hashlib


def pp(data: dict):
    print(json.dumps(data, indent=2))


def gen_webhook(name, code, username, after=None, before=None, ref="refs/heads/master", org="os3224"):
    if after is None:
        after = gen_commit()

    if before is None:
        before = gen_commit()

    return {
        "ref": ref,
        "repository": {
            "url": f"https://github.com/{org}/{name}-{code}-{username}",
            "name": f"{name}-{code}-{username}",
        },
        "pusher": {
            "name": f"{username}",
        },
        "after": after,
        "before": before,

    }


def post_webhook(webhook):
    return requests.post(
        'http://localhost/api/public/webhook/',
        json=webhook,
        headers={'Content-Type': 'application/json', 'X-GitHub-Event': 'push'},
    )


def gen_commit():
    return hashlib.sha256(os.urandom(12)).hexdigest()[:40]


@app_context
def test_webhooks():
    assignment = Assignment.query.first()

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, "wabscale", "0" * 40, "0" * 40)).json()
    assert r['data'] == 'initial commit'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, "wabscale")).json()
    assert r['data'] != 'initial commit'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code + 'abc', "wabscale")).json()
    assert r['data'] is None
    assert r['error'] == 'assignment not found'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, "wabscale", ref="abc123")).json()
    assert r['error'] == 'not push to master'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, gen_commit())).json()
    assert r['error'] == 'dangling submission'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, "wabscale")).json()
    assert r['data'] == 'submission accepted'


if __name__ == '__main__':
    test_webhooks()
