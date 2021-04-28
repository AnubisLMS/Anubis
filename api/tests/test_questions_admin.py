from utils import Session, permission_test

sample_question = {
    'question': 'question',
    'solution': 'solution',
    'code_language': 'markdown',
    'code_question': True,
    'sequence': 0,
}


def test_questions_admin():
    superuser = Session('superuser')
    professor = Session('professor')
    student = Session('student')
    ta = Session('ta')

    unique_code = superuser.get('/admin/assignments/list')['assignments'][0]['unique_code']
    superuser.get(f'/admin/questions/reset-assignments/{unique_code}')

    permission_test(f'/admin/questions/get/{unique_code}')
    permission_test(f'/admin/questions/get-assignments/{unique_code}')

    permission_test(f'/admin/questions/add/{unique_code}')
    permission_test(f'/admin/questions/add/{unique_code}')
    questions = superuser.get(f'/admin/questions/get/{unique_code}')['questions']
    print(questions)
    question_id = questions['0'][0]['id']
    permission_test(f'/admin/questions/update/{question_id}', method='post', json={'question': sample_question})

    superuser.get(f'/admin/questions/delete/{questions["0"][0]["id"]}')
    professor.get(f'/admin/questions/delete/{questions["0"][1]["id"]}')
    ta.get(f'/admin/questions/delete/{questions["0"][2]["id"]}')
    student.get(f'/admin/questions/delete/{questions["0"][3]["id"]}', should_fail=True)

    permission_test(f'/admin/questions/add/{unique_code}')
    superuser.get(f'/admin/questions/reset-assignments/{unique_code}')
    permission_test(
        f'/admin/questions/assign/{unique_code}',
        after=lambda: superuser.get(f'/admin/questions/reset-assignments/{unique_code}')
    )

    superuser.get(f'/admin/questions/reset-assignments/{unique_code}')
    permission_test(f'/admin/questions/reset-assignments/{unique_code}', fail_for=['student', 'ta'])
    permission_test(f'/admin/questions/hard-reset/{unique_code}', fail_for=['student', 'ta'])
