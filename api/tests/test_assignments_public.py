from utils import Session


def test_assignment_public():
    s = Session('student')
    s.get('/public/assignments/')
    s.get('/public/assignments/list')
    
    s = Session('superuser')
    s.get('/public/assignments/')
    s.get('/public/assignments/list')

