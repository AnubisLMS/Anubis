from utils import Session, permission_test

sample_question = {
    "question": "question",
    "solution": "solution",
    "code_language": "markdown",
    "code_question": True,
    "pool": 0,
}


def test_questions_admin():
    superuser = Session("superuser")
    professor = Session("professor")
    student = Session("student")
    ta = Session("ta")

    assignment_id = superuser.get("/admin/assignments/list")["assignments"][0]["id"]
    superuser.get(f"/admin/questions/reset-assignments/{assignment_id}")

    permission_test(f"/admin/questions/get/{assignment_id}")
    permission_test(f"/admin/questions/get-assignments/{assignment_id}")

    permission_test(f"/admin/questions/add/{assignment_id}")
    permission_test(f"/admin/questions/add/{assignment_id}")
    questions = superuser.get(f"/admin/questions/get/{assignment_id}")["questions"]
    print(questions)
    question_id = questions[0]["id"]
    permission_test(
        f"/admin/questions/update/{question_id}",
        method="post",
        json={"question": sample_question},
    )

    superuser.get(f'/admin/questions/delete/{questions[0]["id"]}')
    professor.get(f'/admin/questions/delete/{questions[1]["id"]}')
    ta.get(f'/admin/questions/delete/{questions[2]["id"]}')
    student.get(f'/admin/questions/delete/{questions[3]["id"]}', should_fail=True)

    permission_test(f"/admin/questions/add/{assignment_id}")
    superuser.get(f"/admin/questions/reset-assignments/{assignment_id}")
    permission_test(
        f"/admin/questions/assign/{assignment_id}",
        after=lambda: superuser.get(f"/admin/questions/reset-assignments/{assignment_id}"),
    )

    superuser.get(f"/admin/questions/reset-assignments/{assignment_id}")
    permission_test(
        f"/admin/questions/reset-assignments/{assignment_id}",
        fail_for=["student", "ta"],
    )
    permission_test(f"/admin/questions/hard-reset/{assignment_id}", fail_for=["student", "ta"])
