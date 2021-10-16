import copy

from utils import Session
from datetime import datetime, timedelta


sample_sync = {
    "name": "CS-UY 3224 TEST PUBLIC HIDDEN 1",
    "course": "CS-UY 3224",
    "hidden": True,
    "github_template": "wabscale/xv6-public",
    "github_repo_required": True,
    "unique_code": "aaaaa1",
    "pipeline_image": "registry.digitalocean.com/anubis/assignment/aa11bb2233",
    "date": {
        "release": str(datetime.now() - timedelta(hours=2)),
        "due": str(datetime.now() + timedelta(hours=12)),
        "grace": str(datetime.now() + timedelta(hours=13)),
    },
    "description": "This is a very long description that encompasses the entire assignment\n",
    "questions": [],
    "tests": ["abc123"],
}
sample_sync_2 = copy.deepcopy(sample_sync)
sample_sync_2['name'] = 'CS-UY 3224 TEST PUBLIC HIDDEN 2'
sample_sync_2['hidden'] = False
sample_sync_2['unique_code'] = 'aaaaa2'
sample_sync_2['date']['release'] = str(datetime.now() + timedelta(hours=2))


def create_hidden_assignments():
    s = Session('superuser')
    s.post_json('/admin/assignments/sync', json={'assignment': sample_sync})
    s.post_json('/admin/assignments/sync', json={'assignment': sample_sync_2})


def test_assignment_public():
    create_hidden_assignments()

    s = Session('student')
    s.get('/public/assignments')
    r = s.get('/public/assignments/list')
    assert all(map(lambda a: a['name'].startswith('CS-UY 3224'), r['assignments']))
    assert any(map(lambda a: a['name'] != 'CS-UY 3224 TEST PUBLIC HIDDEN 1', r['assignments']))
    assert any(map(lambda a: a['name'] != 'CS-UY 3224 TEST PUBLIC HIDDEN 2', r['assignments']))

    s = Session('ta')
    r = s.get('/public/assignments')
    assert all(map(lambda a: a['name'].startswith('CS-UY 3224'), r['assignments']))
    assert any(map(lambda a: a['name'] == 'CS-UY 3224 TEST PUBLIC HIDDEN 1', r['assignments']))
    assert any(map(lambda a: a['name'] == 'CS-UY 3224 TEST PUBLIC HIDDEN 2', r['assignments']))

    s = Session('superuser')
    r = s.get('/public/assignments')
    assert any(map(lambda a: a['name'].startswith('CS-UY 3224'), r['assignments']))
    assert any(map(lambda a: a['name'].startswith('CS-UY 3843'), r['assignments']))
    assert any(map(lambda a: a['name'] == 'CS-UY 3224 TEST PUBLIC HIDDEN 1', r['assignments']))
    assert any(map(lambda a: a['name'] == 'CS-UY 3224 TEST PUBLIC HIDDEN 2', r['assignments']))
