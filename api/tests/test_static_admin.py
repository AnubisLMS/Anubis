import io

import requests

from utils import Session


def test_static_admin():
    logo = open('logo.png', 'rb').read()
    filename = 'logo.png'

    student = Session('student')
    logo_file = io.BytesIO(logo)
    student.post('/admin/static/upload', files={filename: logo_file}, should_fail=True)

    prof = Session('professor')
    for _ in range(5):
        logo_file = io.BytesIO(logo)
        prof.post('/admin/static/upload', files={filename: logo_file})
        prof.get('/admin/static/list')

    ta = Session('ta')
    for _ in range(5):
        logo_file = io.BytesIO(logo)
        ta.post('/admin/static/upload', files={filename: logo_file})
        ta.get('/admin/static/list')

    su = Session('superuser')
    for _ in range(5):
        logo_file = io.BytesIO(logo)
        su.post('/admin/static/upload', files={filename: logo_file})
        su.get('/admin/static/list')
