from utils import Session


def test_playground_start():
    s = Session("student", new=True)
    r = s.get("/public/playgrounds/active")
    assert r == {"active": False}

    r = s.get("/public/playgrounds/images")
    images = r['images']

    for image in images:
        image_id = image['id']
        r = s.post(f"/public/playgrounds/initialize/{image_id}")
        assert r['session']
        ide_id = r['session']['id']

        r = s.get(f"/public/ide/stop/{ide_id}")
        assert r['status'] == 'Session stopped.'

