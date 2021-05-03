from utils import Session


def test_visuals_public():
    student = Session('student')
    usage = student.get('/public/visuals/usage', return_request=True, skip_verify=True)
    assert usage.status_code == 200

    student.get('/public/visuals/raw-usage')
