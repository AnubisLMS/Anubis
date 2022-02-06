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
            f"/public/visuals/usage/{course_id}",
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
        f"/public/visuals/usage/playgrounds",
        return_request=True,
        skip_verify=True,
    )

    # Just make sure it didn't 500
    assert usage.headers['Content-Type'] == 'image/png'
    assert usage.status_code == 200


def test_visuals_public_active():
    student = Session("student")

    # Get the course visual
    usage = student.get(
        f"/public/visuals/usage/active",
        return_request=True,
        skip_verify=True,
    )

    # Just make sure it didn't 500
    assert usage.headers['Content-Type'] == 'image/png'
    assert usage.status_code == 200
