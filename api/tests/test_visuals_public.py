from tests.utils import Session


def test_visuals_public():
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
        assert usage.status_code == 200
