import random

import pytest

from utils import Session, permission_test

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
