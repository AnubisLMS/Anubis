from utils import Session, permission_test


def test_students_admin():
    student = Session("student", new=True)
    student_id = student.get("/public/auth/whoami")["user"]["id"]

    permission_test("/super/students/list", fail_for=["student", "ta", "professor"],)
    permission_test(
        f"/super/students/toggle-superuser/{student_id}",
        fail_for=["student", "ta", "professor"],
    )
    permission_test(
        f"/super/students/toggle-anubis_developer/{student_id}",
        fail_for=["student", "ta", "professor"],
    )
    permission_test(
        f"/super/students/pvc/{student_id}",
        fail_for=["student", "ta", "professor"],
    )
