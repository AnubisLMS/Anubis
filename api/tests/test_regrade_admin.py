from utils import Session, permission_test, with_context
from anubis.models import Submission


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
    superuser = Session('superuser')
    assignments = superuser.get('/admin/assignments/list')['assignments']
    assignment_ids = list(map(lambda x: x['id'], assignments))
    commit, assignment_id = get_student_submission_commit(assignment_ids)

    permission_test(f'/admin/regrade/status/{assignment_id}')
    permission_test(f'/admin/regrade/submission/{commit}')
    permission_test(f'/admin/regrade/assignment/{assignment_id}')
