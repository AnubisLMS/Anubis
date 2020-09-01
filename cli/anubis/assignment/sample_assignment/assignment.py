from utils import exec_as_student, register_test, register_build
from utils import TestResult, BuildResult, Panic, DEBUG
import os


if DEBUG:
    os.environ['GIT_REPO'] = 'https://github.com/juan-punchman/xv6-public.git'
    os.environ['TOKEN'] = 'null'
    os.environ['COMMIT'] = 'null'
    os.environ['SUBMISSION_ID'] = 'null'


@register_build
def build(build_result: BuildResult):
    build_result.stdout, retcode = exec_as_student('make xv6.img fs.img')
    build_result.passed = retcode == 0

    if b'this is a bad thing' in build_result.stdout:
        raise Panic("This is a bad thing that just happened. "
        "We need to stop this test right here and now")


@register_test('Long file test')
def test_1(test_result: TestResult):
    test_result.stdout, retcode = exec_as_student('echo test command')
    test_result.passed = retcode == 0
    test_result.message = 'Your submission passed this test!'


@register_test('Short file test')
def test_1(test_result: TestResult):
    test_result.stdout, retcode = exec_as_student('echo test command')
    test_result.passed = retcode == 0
    test_result.message = 'Your submission passed this test too!'
