from tests.utils import Session, permission_test


def test_visuals_admin():
    superuser = Session("superuser")
    assignment_id = superuser.get("/admin/assignments/list")["assignments"][0]["id"]

    # student = Session('student')
    # student.get(f'/admin/visuals/assignment/{assignment_id}', should_fail=True)

    # permission_test(f'/admin/visuals/assignment/{assignment_id}')
    permission_test(f"/admin/visuals/sundial/{assignment_id}")
    permission_test(f"/admin/visuals/history/{assignment_id}/superuser")
