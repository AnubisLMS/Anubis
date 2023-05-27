import pytest

from anubis.models import Submission
from utils import Session, permission_test, with_context


@with_context
def get_student_submission_commit(assignment_ids):
    for assignment_id in assignment_ids:
        submission = Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id != None,
        ).first()
        if submission is not None:
            return submission.commit, assignment_id


def test_regrade_admin():
    superuser = Session("superuser")
    assignments = superuser.get("/admin/assignments/list")["assignments"]
    assignment_ids = list(map(lambda x: x["id"], assignments))
    commit, assignment_id = get_student_submission_commit(assignment_ids)

    permission_test(f"/admin/regrade/status/{assignment_id}")
    permission_test(f"/admin/regrade/submission/{commit}")
    permission_test(f"/admin/regrade/assignment/{assignment_id}")


@pytest.mark.timeout(40)
def test_regrade_admin_student():
    superuser = Session("superuser")
    # Get list of students
    students = superuser.get("/admin/students/list")["students"]
    assert len(students) > 0
    student_id = students[0]["id"]

    # Permission tests
    permission_test(f"/admin/regrade/student/{student_id}", method="post", json={})
    permission_test(f"/admin/regrade/status/student/{student_id}")

    # Test Submissions pipeline
    resp = superuser.post(f"/admin/regrade/student/{student_id}")
    assert resp["status"] == "Regrade enqueued."

    # get the status of the regrade for a student and make sure they get fully processed
    status = superuser.get(f"/admin/regrade/status/student/{student_id}")

    # make sure total is greater than 0 (meaning it has actually been enqueued)
    assert status["total"] > 0
