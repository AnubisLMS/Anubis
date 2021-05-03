from utils import Session


def test_courses_public():
    s = Session('student')
    s.get('/public/courses/')
    courses = s.get('/public/courses/list')['courses']
    join_code = courses[0]['join_code']

    sn = Session('student', new=True, add_to_os=False)
    courses = sn.get('/public/courses/list')['courses']
    assert len(courses) == 0
    sn.get(f'/public/courses/join/aaa', should_fail=True)
    sn.get(f'/public/courses/join/{join_code}')
    courses = sn.get('/public/courses/list')['courses']
    assert len(courses) == 1
