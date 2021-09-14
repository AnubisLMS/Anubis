import io

import requests

from utils import Session


def test_static_public():
    # Upload image as a professor first so we have a image to test downloading
    logo = open('logo.png', 'rb').read()
    filename = 'logo.png'
    prof = Session('professor')
    logo_file = io.BytesIO(logo)
    blob_id = prof.post('/admin/static/upload', files={filename: logo_file})['blob']['path'].lstrip('/')

    # Now test as a student
    student = Session('student')
    r = student.get(f'/public/static/{blob_id}', return_request=True, skip_verify=True)
    assert r.status_code == 200
    assert r.headers.get('content-type') == 'image/png'

    r = student.get(f'/public/static/{blob_id}/logo.png', return_request=True, skip_verify=True)
    assert r.status_code == 200
    assert r.headers.get('content-type') == 'image/png'

    r = student.get(f'/public/static/{blob_id}/logo.pn', return_request=True, skip_verify=True)
    assert r.status_code == 404
    assert r.text.startswith('404 Not Found :(')
