from tests.utils import Session


def test_courses_public():
    s = Session("student")
    s.get("/public/courses/")
    courses = s.get("/public/courses/list")["courses"]
    join_code = courses[0]["join_code"]
    id = courses[0]["id"]

    sn = Session("student", new=True, add_to_os=False)
    courses = sn.get("/public/courses/list")["courses"]
    assert len(courses) == 0
    sn.get(f"/public/courses/join/aaa", should_fail=True)
    sn.get(f"/public/courses/join/{join_code}")
    courses = sn.get("/public/courses/list")["courses"]
    assert len(courses) == 1
    sn.get("/public/courses/get/12345", should_fail=True)
    course = sn.get(f"/public/courses/get/{id}")["course"]
    assert course

