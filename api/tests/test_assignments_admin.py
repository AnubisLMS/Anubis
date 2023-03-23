import math
import random
from datetime import timedelta

import pytest
from utils import Session, permission_test, with_context

from anubis.lms.submissions import fix_submissions_for_autograde_disabled_assignment
from anubis.models import Assignment, Submission, db
from anubis.models.id import default_id_factory
from anubis.utils.testing.seed import rand_commit

sample_sync = {
    "name":           "CS-UY 3224 TEST ADMIN",
    "course":         "CS-UY 3224",
    "unique_code":    "aa11bb22",
    "pipeline_image": "registry.digitalocean.com/anubis/assignment/aa11bb2233",
    "tests":          [
        {"name": "a1", "hidden": False, "points": 10},
        {"name": "b2", "hidden": True, "points": 10},
        {"name": "c3", "hidden": False, "points": 20},
    ],
}


def test_assignment_admin():
    superuser = Session("superuser")

    permission_test("/admin/assignments/list")

    for assignment_ in superuser.get("/admin/assignments/list")['assignments']:
        if assignment_['name'] == 'CS-UY 3224 Assignment 4':
            assignment = assignment_
            break
    else:
        assert False

    assignment_id = assignment["id"]
    _tests = superuser.get(f"/admin/assignments/get/{assignment_id}")["tests"]
    assignment_test_id = _tests[0]["id"]

    permission_test(f"/admin/assignments/get/{assignment_id}")
    permission_test(f"/admin/assignments/assignment/{assignment_id}/questions/get/student")
    permission_test(f"/admin/assignments/tests/toggle-hide/{assignment_test_id}")
    permission_test(f"/admin/assignments/save", method="post", json={"assignment": assignment})
    permission_test(f"/admin/assignments/sync", method="post", json={"assignment": sample_sync})


@pytest.mark.parametrize("add_questions,assign_questions,add_responses", [
    (False, False, False),
    (True, False, False),
    (True, True, False),
    (True, True, True),
])
def test_assignment_delete(add_questions, assign_questions, add_responses):
    superuser = Session("superuser")
    student = Session("student", new=True, add_to_os=True)

    assignment = superuser.post('/admin/assignments/add')['assignment']
    assignment_id = assignment['id']
    assert assignment_id is not None

    if add_questions:
        for pool in range(5):
            for question_n in range(random.randint(3, 4)):
                question = superuser.get(f'/admin/questions/add/{assignment_id}')['question']
                question_id = question['id']
                question_data = {
                    'question':      f'pool={pool} question={question_n}',
                    'solution':      'solution',
                    'code_language': '',
                    'code_question': False,
                    'pool':          pool
                }
                superuser.post_json(f'/admin/questions/update/{question_id}', json={'question': question_data})

    if assign_questions:
        assigned = superuser.get(f'/admin/questions/assign/{assignment_id}')
        assert assigned['status'] == 'Questions assigned'

    if add_responses:
        questions = student.get(f'/public/questions/get/{assignment_id}')['questions']
        assert len(questions) == 5

        response = []
        for pool in range(5):
            response.append({
                'question': questions[pool],
                'response': {'text': f'response {pool}'},
                'id':       questions[pool]['id']
            })
        save = student.post_json(f'/public/questions/save/{assignment_id}', json={'questions': response})
        assert save['status'] == 'Response Saved'

    superuser.delete(f'/admin/assignments/delete/{assignment_id}')

    assignments = superuser.get(f'/admin/assignments/list')['assignments']
    for assignment_ in assignments:
        assert assignment_['id'] != assignment_id

@with_context
def test_fix_late_autograde_disabled_assignments(caplog):
    assignment = Assignment.query.filter(Assignment.name == "CS-UY 3224 Assignment 3")
    assignment.update(
        {
            "accept_late": False,
            "autograde_enabled": False,
        }
    )
    assignment = assignment.first()
    assert assignment is not None

    # All test submissions will be created using this submission's owner
    ref_submission: Submission = Submission.query.filter(Submission.assignment_id == assignment.id).first()
    assert ref_submission is not None

    def create_submission(late: bool, accepted: bool):
        created = assignment.grace_date
        if late:
            created += timedelta(hours=math.sqrt(5))
        else:
            created -= timedelta(hours=math.sqrt(5))

        return Submission(
            id=default_id_factory(),
            commit=rand_commit(),
            state="Waiting for resources...",
            owner=ref_submission.owner,
            assignment_id=assignment.id,
            created=created,
            accepted=accepted,
        )

    late_accepted = create_submission(late=True, accepted=True)
    late_not_accepted = create_submission(late=True, accepted=False)
    ontime_accepted = create_submission(late=False, accepted=True)
    ontime_not_accepted = create_submission(late=False, accepted=False)

    fix_submissions_for_autograde_disabled_assignment(assignment)

    assert len(caplog.records) == 2
    assert "Fixed 1 falsely accepted" in caplog.records[1].msg

    assert late_not_accepted.accepted == False
    assert late_accepted.accepted == False
    assert ontime_accepted.accepted == True
    assert ontime_not_accepted.accepted == False
