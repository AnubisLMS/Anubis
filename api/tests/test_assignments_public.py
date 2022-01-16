import copy
from datetime import datetime, timedelta

from utils import Session, with_context

sample_sync = {
    "name": "CS-UY 3224 TEST PUBLIC HIDDEN 1",
    "course": "CS-UY 3224",
    "unique_code": "aaaaa1",
    "pipeline_image": "registry.digitalocean.com/anubis/assignment/aa11bb2233",
    "tests": [{"name": "abc123", "hidden": False, "points": 10}],
}
sample_sync_2 = copy.deepcopy(sample_sync)
sample_sync_2["name"] = "CS-UY 3224 TEST PUBLIC HIDDEN 2"
sample_sync_2["unique_code"] = "aaaaa2"


@with_context
def update_hidden_assignments(aid1, aid2):
    from anubis.models import db, Assignment
    db.session.expire_all()
    db.session.expunge_all()

    assignment1: Assignment = Assignment.query.filter(Assignment.id == aid1).first()
    assignment2: Assignment = Assignment.query.filter(Assignment.id == aid2).first()

    assignment1.hidden = True
    assignment1.release_date = datetime.now() - timedelta(hours=2)
    assignment2.hidden = False
    assignment2.release_date = datetime.now() + timedelta(hours=2)

    db.session.commit()


def create_hidden_assignments():
    s = Session("superuser")

    d1 = s.post_json("/admin/assignments/sync", json={"assignment": sample_sync})
    d2 = s.post_json("/admin/assignments/sync", json={"assignment": sample_sync_2})

    update_hidden_assignments(d1['assignment']['id'], d2['assignment']['id'])


def test_assignment_public():
    create_hidden_assignments()

    s = Session("student")
    s.get("/public/assignments")
    r = s.get("/public/assignments/list")
    assert all(map(lambda a: a["name"].startswith("CS-UY 3224"), r["assignments"]))
    assert any(map(lambda a: a["name"] != "CS-UY 3224 TEST PUBLIC HIDDEN 1", r["assignments"]))
    assert any(map(lambda a: a["name"] != "CS-UY 3224 TEST PUBLIC HIDDEN 2", r["assignments"]))

    s = Session("ta")
    r = s.get("/public/assignments")
    assert all(map(lambda a: a["name"].startswith("CS-UY 3224"), r["assignments"]))
    assert any(map(lambda a: a["name"] == "CS-UY 3224 TEST PUBLIC HIDDEN 1", r["assignments"]))
    assert any(map(lambda a: a["name"] == "CS-UY 3224 TEST PUBLIC HIDDEN 2", r["assignments"]))

    s = Session("superuser")
    r = s.get("/public/assignments")
    assert any(map(lambda a: a["name"].startswith("CS-UY 3224"), r["assignments"]))
    assert any(map(lambda a: a["name"].startswith("CS-UY 3843"), r["assignments"]))
    assert any(map(lambda a: a["name"] == "CS-UY 3224 TEST PUBLIC HIDDEN 1", r["assignments"]))
    assert any(map(lambda a: a["name"] == "CS-UY 3224 TEST PUBLIC HIDDEN 2", r["assignments"]))
