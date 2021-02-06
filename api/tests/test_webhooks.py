import json

import requests

from utils import app_context, do_seed
from anubis.models import db, User, Assignment, AssignmentRepo, Submission, InCourse, Course
import os
import hashlib


def pp(data: dict):
    print(json.dumps(data, indent=2))


def gen_webhook(name, code, username, after=None, before=None, ref="refs/heads/master", org="os3224"):
    if after is None:
        after = gen_rand(40)

    if before is None:
        before = gen_rand(40)

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
        'http://localhost:5000/public/webhook/',
        json=webhook,
        headers={'Content-Type': 'application/json', 'X-GitHub-Event': 'push'},
    )


def gen_rand(n: int = 40):
    return hashlib.sha256(os.urandom(12)).hexdigest()[:n]


@app_context
def create_user(github_username: str):
    u = User(netid=gen_rand(6), name=gen_rand(6), github_username=github_username)
    c = Course.query.first()
    ic = InCourse(course=c, owner=u)
    db.session.add_all([u, ic])
    db.session.commit()
    return u.github_username


@app_context
def do_webhook_tests_user(github_username):
    user = User.query.filter_by(github_username=github_username).first()

    import pymysql
    connection = pymysql.connect(host='localhost',
                                 user='anubis',
                                 password='anubis',
                                 database='anubis',
                                 charset='utf8mb4')

    assignment = Assignment.query.first()
    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, user.github_username, "0" * 40, "0" * 40)).json()
    assert r['data'] == 'initial commit'
    with connection.cursor() as cursor:
        cursor.execute(
            'select * from assignment_repo where assignment_id = %s and owner_id = %s;',
            (assignment.id, user.id)
        )
        assert cursor.fetchone() is not None
        cursor.execute(
            'select count(id) from assignment_repo where assignment_id = %s and owner_id = %s;',
            (assignment.id, user.id)
        )
        count = cursor.fetchone()
        assert count is not None and count[0] == 1

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, user.github_username)).json()
    assert r['data'] != 'initial commit'
    with connection.cursor() as cursor:
        cursor.execute(
            'select * from assignment_repo where assignment_id = %s and owner_id = %s;',
            (assignment.id, user.id)
        )
        assert cursor.fetchone() is not None
        cursor.execute(
            'select count(id) from assignment_repo where assignment_id = %s and owner_id = %s;',
            (assignment.id, user.id)
        )
        count = cursor.fetchone()
        assert count is not None and count[0] == 1

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code + 'abc', user.github_username)).json()
    assert r['data'] is None
    assert r['error'] == 'assignment not found'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, user.github_username, ref="abc123")).json()
    assert r['error'] == 'not push to master'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, gen_rand(6))).json()
    assert r['error'] == 'dangling submission'

    r = post_webhook(gen_webhook(assignment.name, assignment.unique_code, user.github_username)).json()
    assert r['data'] == 'submission accepted'

    connection.close()


def test_webhooks():
    do_seed()

    username1 = create_user(f'abc123')
    username2 = create_user(f'{gen_rand(3)}-{gen_rand(3)}')

    do_webhook_tests_user('wabscale')
    do_webhook_tests_user(username1)
    do_webhook_tests_user(username2)


if __name__ == '__main__':
    test_webhooks()
