import io

import requests

from utils import Session


def test_lectures_admin():
    logo = requests.get('https://linux.org/images/logo.png').content
    filename = 'logo.png'

    su = Session('superuser')

    # Test uploading lecture file
    logo_file = io.BytesIO(logo)
    su.post(
        '/admin/lectures/upload',
        params={'number': 1, 'title': 'test', 'description': 'description'},
        files={filename: logo_file},
    )
    su.get('/admin/lectures/list')
