from utils import Session


def test_visuals_public_course():
    student = Session("student")

    # Get all course data with visuals enabled
    courses_with_visuals = student.get("/public/courses/visuals-list")["courses"]

    # Iterate over courses, generating visuals for each
    for course in courses_with_visuals:

        # Pull course id
        course_id = course["id"]

        # Get the course visual
        usage = student.get(
            f"/public/visuals/course/{course_id}",
            return_request=True,
            skip_verify=True,
        )

        # Just make sure it didn't 500
        assert usage.headers['Content-Type'] == 'image/png'
        assert usage.status_code == 200


def test_visuals_public_playgrounds():
    student = Session("student")

    # Get the course visual
    usage = student.get(
        f"/public/visuals/playgrounds",
        return_request=True,
        skip_verify=True,
    )

    # Just make sure it didn't 500
    assert usage.headers['Content-Type'] == 'image/png'
    assert usage.status_code == 200


def test_visuals_public_active():
    student = Session("student")

    for days, step in [(14, 1), (90, 7), (180, 1), (365, 30)]:
        # Get the course visual
        usage = student.get(
            f"/public/visuals/active/{days}/{step}",
            return_request=True,
            skip_verify=True,
        )

        # Just make sure it didn't 500
        assert usage.headers['Content-Type'] == 'image/png'
        assert usage.status_code == 200


def test_visuals_public_users():
    student = Session("student")

    for days, step in [(365, 1), (365, 30)]:
        # Get the course visual
        r = student.get(
            f"/public/visuals/users/{days}/{step}",
            return_request=True,
            skip_verify=True,
        )

        # Just make sure it didn't 500
        print('aaa', r.content)
        assert r.headers['Content-Type'] == 'image/png'
        assert r.status_code == 200
