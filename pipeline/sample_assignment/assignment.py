from utils import exec_as_student, register_test, TestResult


@register_test('First test')
def test_1(test_result: TestResult):
    test_result.stdout, _ = exec_as_student('echo test command')
    test_result.passed = True
    test_result.message = 'Your submission passed this test!'
