from tests.utils import Session, get_student_id, permission_test


def test_autograde_admin():
    superuser = Session("superuser")
    assignment_id = superuser.get("/admin/assignments/list")["assignments"][0]["id"]
    student_id = get_student_id()

    permission_test(f"/admin/autograde/assignment/{assignment_id}")
    permission_test(f"/admin/autograde/for/{assignment_id}/{student_id}")
    permission_test(f"/admin/autograde/submission/{assignment_id}/student")
