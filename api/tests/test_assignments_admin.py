from datetime import datetime, timedelta

from utils import Session, permission_test

sample_sync = {
    "name": "CS-UY 3224 TEST ADMIN",
    "course": "CS-UY 3224",
    "unique_code": "aa11bb22",
    "pipeline_image": "registry.digitalocean.com/anubis/assignment/aa11bb2233",
    "tests": [
        {"name": "a1", "hidden": False, "points": 10},
        {"name": "b2", "hidden": True, "points": 10},
        {"name": "c3", "hidden": False, "points": 20},
    ],
}


def test_assignment_admin():
    superuser = Session("superuser")

    permission_test("/admin/assignments/list")

    assignment = superuser.get("/admin/assignments/list")["assignments"][0]
    assignment_id = assignment["id"]
    _tests = superuser.get(f"/admin/assignments/get/{assignment_id}")["tests"]
    assignment_test_id = _tests[0]["id"]

    permission_test(f"/admin/assignments/get/{assignment_id}")
    permission_test(f"/admin/assignments/assignment/{assignment_id}/questions/get/student")
    permission_test(f"/admin/assignments/tests/toggle-hide/{assignment_test_id}")
    permission_test(f"/admin/assignments/save", method="post", json={"assignment": assignment})
    permission_test(f"/admin/assignments/sync", method="post", json={"assignment": sample_sync})
