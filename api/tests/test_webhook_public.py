import hashlib
import json
import os

import requests

from anubis.models import Assignment, Course, InCourse, User, db
from anubis.utils.data import with_context


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
        "http://localhost:5000/public/webhook/",
        json=webhook,
        headers={"Content-Type": "application/json", "X-GitHub-Event": "push"},
    )


def gen_rand(n: int = 40):
    return hashlib.sha256(os.urandom(12)).hexdigest()[:n]


@with_context
def create_user(github_username: str):
    u = User(netid=gen_rand(6), name=gen_rand(6), github_username=github_username)
    c = Course.query.filter(Course.name == "Intro to OS").first()
    ic = InCourse(course=c, owner=u)
    db.session.add_all([u, ic])
    db.session.commit()
    return u.github_username


@with_context
def do_webhook_tests_user(github_username):
    user = User.query.filter_by(github_username=github_username).first()
    assignment = Assignment.query.join(Course).filter(Course.name == "Intro to OS").first()

    assignment_id = assignment.id
    assignment_name = assignment.name
    assignment_unique_code = assignment.unique_code
    user_id = user.id
    user_github_username = user.github_username

    print(db.engine)
    print(assignment_name, assignment_unique_code)

    db.session.expire_all()
    r = post_webhook(
        gen_webhook(
            assignment_name,
            assignment_unique_code,
            user_github_username,
            "0" * 40,
            "0" * 40,
        )
    ).json()
    assert r["data"] == "initial commit"
    db.session.expire_all()
    response = db.engine.execute(
        "select count(id) from assignment_repo where assignment_id = '{}' and owner_id = '{}';".format(
            assignment_id, user_id
        )
    )
    assert response.fetchone()[0] == 1

    r = post_webhook(gen_webhook(assignment_name, assignment_unique_code, user_github_username)).json()
    db.session.expire_all()
    assert r["data"] != "initial commit"
    response = db.engine.execute(
        "select count(id) from assignment_repo where assignment_id = '{}' and owner_id = '{}';".format(
            assignment_id, user_id
        )
    )
    assert response.fetchone()[0] == 1

    r = post_webhook(gen_webhook(assignment_name, assignment_unique_code + "abc", user_github_username)).json()
    assert r["data"] is None
    assert r["error"] == "assignment not found"

    r = post_webhook(gen_webhook(assignment_name, assignment_unique_code, user_github_username, ref="abc123")).json()
    assert r["error"] == "not a push to master or main"

    r = post_webhook(gen_webhook(assignment_name, assignment_unique_code, gen_rand(6))).json()
    assert r["error"] == "dangling submission"

    r = post_webhook(gen_webhook(assignment_name, assignment_unique_code, user_github_username)).json()
    assert r["data"] == "submission accepted"


def test_webhooks():
    username1 = create_user(f"{gen_rand(3)}-{gen_rand(3)}")
    username2 = create_user(f"{gen_rand(3)}-{gen_rand(3)}")

    do_webhook_tests_user(username1)
    do_webhook_tests_user(username2)


if __name__ == "__main__":
    test_webhooks()
