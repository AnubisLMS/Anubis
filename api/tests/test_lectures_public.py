import io

import requests

from utils import Session


def test_lectures_public():
    # upload a lecture as a superuser
    logo = open("logo.png", "rb").read()
    filename = "logo.png"
    su = Session("superuser")
    logo_file = io.BytesIO(logo)
    su.post(
        "/admin/lectures/upload",
        params={"number": 1, "title": "test", "description": "description"},
        files={filename: logo_file},
    )

    student = Session("student")
    student.get("/public/lectures/list")
