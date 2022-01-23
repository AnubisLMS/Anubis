from utils import Session


def test_questions_public():
    s = Session("student")
    assignment_id = s.get("/public/assignments/list")["assignments"][0]["id"]

    questions = s.get(f"/public/questions/get/{assignment_id}")["questions"]
    s.get(f"/public/questions/get/notanid", should_fail=True)

    questions[0]['response'] = {'text': ''}
    s.post_json(f"/public/questions/save/{assignment_id}", json={"questions": questions})

    questions[0]['response'] = {'text': 1}
    s.post_json(f"/public/questions/save/{assignment_id}", json={"questions": questions}, should_fail=True)

    questions[0]['response'] = {'text': None}
    s.post_json(f"/public/questions/save/{assignment_id}", json={"questions": questions})
