from utils import Session, permission_test


def test_students_admin():
    student = Session('student', new=True)
    student_id = student.get('/public/auth/whoami')['user']['id']

    permission_test('/admin/students/list')
    permission_test('/admin/students/list/basic')
    permission_test(f'/admin/students/info/{student_id}')
    permission_test(f'/admin/students/submissions/{student_id}')
    permission_test(f'/admin/students/update/{student_id}', method='post', json={
        'name': 'student', 'github_username': 'student',
    }, fail_for=['student', 'ta'])
    permission_test(f'/admin/students/toggle-superuser/{student_id}', fail_for=['student', 'ta', 'professor'])


