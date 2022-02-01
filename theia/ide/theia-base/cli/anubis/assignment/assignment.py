from utils import (
    TestResult, BuildResult, Panic, xv6_run, did_xv6_crash, verify_expected,
    register_test, register_build, hide_test, points_test, exec_as_student, search_lines, test_lines
)


@register_build
def build(build_result: BuildResult):
    stdout, retcode = exec_as_student('make xv6.img fs.img')

    build_result.stdout = stdout
    build_result.passed = retcode == 0

    if 'this is a bad thing' in stdout:
        raise Panic("This is a bad thing that just happened. "
                    "We need to stop this pipeline right here and now")


@register_test('Long file test')
@points_test(10)
def test_1(test_result: TestResult):
    test_result.message = "Testing long lines\n"

    # Start xv6 and run command
    stdout_lines = xv6_run("echo 123", test_result)

    # Run echo 123 as student user and capture output lines
    expected_raw, _ = exec_as_student('echo 123')
    expected = expected_raw.strip().split('\n')

    # Attempt to detect crash
    if did_xv6_crash(stdout_lines, test_result):
        return

    # Test to see if the expected result was found
    verify_expected(stdout_lines, expected, test_result)


@register_test('grep test')
@hide_test()
@points_test(10)
def test_2(test_result: TestResult):
    test_result.message = "Testing long lines\n"

    # Start xv6 and run command
    stdout_lines = xv6_run("grep the README.md", test_result)

    # Run echo 123 as student user and capture output lines
    expected_raw, _ = exec_as_student('grep the README.md')
    expected = expected_raw.strip().split('\n')

    # Attempt to detect crash
    if did_xv6_crash(stdout_lines, test_result):
        return

    # Test to see if the expected result was found
    verify_expected(stdout_lines, expected, test_result)
