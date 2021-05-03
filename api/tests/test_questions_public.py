from utils import Session


def test_questions_public():
    s = Session('student')
    assignment_id = s.get('/public/assignments/list')['assignments'][0]['id']

    questions = s.get(f'/public/questions/get/{assignment_id}')['questions']
    s.get(f'/public/questions/get/notanid', should_fail=True)

    for index, question in enumerate(questions):
        question_id = question['id']
        s.post_json(
            f'/public/questions/save/{question_id}',
            json={'response': 'test123'}
        )
        s.post_json(
            f'/public/questions/save/{question_id}',
            json={'response': 1}, should_fail=True,
        )
        s.post_json(
            f'/public/questions/save/{question_id}',
            json={'response': None}, should_fail=True,
        )
        _questions = s.get(f'/public/questions/get/{assignment_id}')['questions']
        assert _questions[index]['response'] == 'test123'
