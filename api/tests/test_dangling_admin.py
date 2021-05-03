from utils import permission_test


def test_dangling_admin():
    permission_test('/admin/dangling/list', fail_for=['student', 'ta', 'professor'])
    permission_test('/admin/dangling/reset', fail_for=['student', 'ta', 'professor'])
    permission_test('/admin/dangling/fix', fail_for=['student', 'ta', 'professor'])
