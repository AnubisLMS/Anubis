import io

import requests


def test_upload():
    logo = requests.get('https://linux.org/images/logo.png').content
    filename = 'logo.png'

    for _ in range(5):
        logo_file = io.BytesIO(logo)
        r = requests.post(
            'http://localhost/api/admin/static/upload',
            files={
                filename: logo_file,
            },
        )

        print(r.text)

        assert r.status_code == 200


if __name__ == '__main__':
    test_upload()
