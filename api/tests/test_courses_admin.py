from utils import Session, permission_test


def test_courses_admin():
    superuser = Session("superuser")
    student = Session("student", new=True)
    student_id = student.get("/public/auth/whoami")["user"]["id"]

    permission_test("/admin/courses/")
    permission_test("/admin/courses/list")

    course = superuser.get("/admin/courses/list")["course"]

    permission_test("/admin/courses/new", fail_for=["student", "ta", "professor"])
    permission_test("/admin/courses/list/tas")
    permission_test("/admin/courses/list/professors")

    permission_test(
        "/admin/courses/save",
        method="post",
        json={"course": course},
        fail_for=[
            "student",
            "ta",
        ],
    )

    permission_test(
        f"/admin/courses/make/ta/{student_id}",
        after=lambda: superuser.get(
            f"/admin/courses/remove/ta/{student_id}",
            skip_verify=True,
            return_request=True,
        ),
    )
    superuser.get(f"/admin/courses/make/ta/{student_id}", skip_verify=True, return_request=True)
    permission_test(
        f"/admin/courses/remove/ta/{student_id}",
        after=lambda: superuser.get(
            f"/admin/courses/make/ta/{student_id}",
            skip_verify=True,
            return_request=True,
        ),
        fail_for=["student", "ta"],
    )

    permission_test(
        f"/admin/courses/make/professor/{student_id}",
        after=lambda: superuser.get(
            f"/admin/courses/remove/professor/{student_id}",
            skip_verify=True,
            return_request=True,
        ),
        fail_for=["student", "ta", "professor"],
    )
    superuser.get(
        f"/admin/courses/make/professor/{student_id}",
        skip_verify=True,
        return_request=True,
    )
    permission_test(
        f"/admin/courses/remove/professor/{student_id}",
        after=lambda: superuser.get(
            f"/admin/courses/make/professor/{student_id}",
            skip_verify=True,
            return_request=True,
        ),
        fail_for=["student", "ta", "professor"],
    )
