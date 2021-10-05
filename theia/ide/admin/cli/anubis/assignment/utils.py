import subprocess
import functools
import warnings
import logging
import typing
import json
import os

DEBUG = os.environ.get('DEBUG', default='0') == '1'

registered_tests = {}
build_function = None


class TestResult(object):
    def __init__(self):
        self.stdout = None
        self.message = None
        self.passed = None

    def __repr__(self):
        return "<TestResult passed={} message={:5.5} stdout={:5.5}>".format(
            self.passed,
            self.message,
            self.stdout
        )


class BuildResult(object):
    def __init__(self):
        self.stdout = None
        self.passed = None

    def __repr__(self):
        return "<BuildResult passed={} stdout={:5.5}>".format(
            self.passed,
            self.stdout
        )


class Panic(Exception):
    pass


def exec_as_student(cmd, timeout=60) -> typing.Tuple[str, int]:
    """
    Run a command as the student. Any and all times that student
    code is run, it should be done through this function. Any other
    way would be incredibly insecure.

    :param cmd: Command to run
    :param timeout: Timeout for command
    :return: bytes output, int return code
    """

    if os.getcwd() == '/home/anubis':
        os.chdir('./student')

    return_code = 0
    try:
        print('{} {}'.format(os.getcwd(), ["env", "-i", "su", "student", "-c", cmd]))
        stdout = subprocess.check_output(
            ["env", "-i", "PATH={}".format(os.environ["PATH"]), "su", "student", "-c", cmd],
            timeout=timeout,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.output
        return_code = e.returncode

    # Normalize stdout to string
    if isinstance(stdout, bytes):
        stdout = stdout.decode('utf-8', 'ignore')

    logging.info('exec_as_student command={} return_code={} stdout={}'.format(
        cmd, return_code, stdout
    ))

    return stdout, return_code


def fix_permissions():
    """
    Fix the file permissions of the student repo

    * DEPRECATED *

    :return:
    """
    warnings.warn('DEPRECATED WARNING: fix_permissions no longer has any affect')


def register_test(test_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper():
            result = TestResult()
            func(result)
            return result

        registered_tests[test_name] = wrapper

        return wrapper

    return decorator


def register_build(func):
    @functools.wraps(func)
    def wrapper():
        result = BuildResult()
        func(result)
        return result

    global build_function
    build_function = wrapper

    return wrapper


def trim(stdout: str) -> typing.List[str]:
    """
    This mess of a function is where we parse out the
    pieces we want from the xv6 output.

    A parsed list of string lines is returned.

    :param stdout:
    :return:
    """
    stdout_lines = stdout.split('\n')
    try:
        stdout_lines = stdout_lines[stdout_lines.index('init: starting sh')+1:]
    except ValueError or IndexError:
        return stdout_lines

    while len(stdout_lines) != 0 and (len(stdout_lines[-1].strip()) == 0 or stdout_lines[-1].strip() == '$'):
        stdout_lines.pop()

    if len(stdout_lines) != 0 and stdout_lines[-1].endswith('$'):
        stdout_lines[-1] = stdout_lines[-1].rstrip('$')

    if len(stdout_lines) != 0 and stdout_lines[0].startswith('$'):
        stdout_lines[0] = stdout_lines[0].lstrip('$').strip()

    for index in range(len(stdout_lines)):
        stdout_lines[index] = stdout_lines[index].strip()

    if len(stdout_lines) != 0 and 'terminating on signal 15' in stdout_lines[-1]:
        stdout_lines.pop()

    if len(stdout_lines) != 0:
        stdout_lines[-1] = stdout_lines[-1].strip('$')

    print(json.dumps(stdout_lines, indent=2))
    return stdout_lines


def search_lines(
        stdout_lines: typing.List[str],
        expected_lines: typing.List[str],
        case_sensitive: bool = True
) -> bool:
    """
    Search lines for expected lines. This will return true if all expected lines are in the
    student standard out lines in order. There can be interruptions in the student standard out.
    This function has the advantage of allowing students to still print out debugging lines
    while their output is still accurately checked for  the expected result.

    >>> search_lines(['a', 'b', 'c'], ['a', 'b', 'c']) -> True
    >>> search_lines(['a', 'debugging', 'b', 'c'], ['a', 'b', 'c']) -> True
    >>> search_lines(['a', 'b'],      ['a', 'b', 'c']) -> False

    * Optionally specify if the equality comparison should be case sensitive *

    :param stdout_lines:
    :param expected_lines:
    :param case_sensitive:
    :return:
    """

    if not case_sensitive:
        stdout_lines = list(map(lambda x: x.lower(), stdout_lines))
    found = []
    for line in expected_lines:
        l = line.strip()
        if not case_sensitive:
            l = l.lower()
        for _aindex, _aline in enumerate(stdout_lines):
            if l in _aline:
                found.append(_aindex)
                break
        else:
            found.append(-1)
    if -1 in found:
        return False
    return list(sorted(found)) == found


def test_lines(
        stdout_lines: typing.List[str],
        expected_lines: typing.List[str],
        case_sensitive: bool = True
) -> bool:
    """
    Test lines for exact equality. Whitespace will be stripped off each line automatically.

    * Optionally specify if the equality comparison should be case sensitive *

    >>> test_lines(['a', 'b', 'c'], ['a', 'b', 'c']) -> True
    >>> test_lines(['a', 'debugging', 'b', 'c'], ['a', 'b', 'c']) -> False
    >>> test_lines(['a', 'b'],      ['a', 'b', 'c']) -> False

    :param stdout_lines: students standard out lines as a list of strings
    :param expected_lines: expected lines as a list of strings
    :param case_sensitive: optional boolean to indicate if comparison should be case sensitive
    :return: True if exact match was found, False otherwise
    """
    if case_sensitive:
        return len(stdout_lines) == len(expected_lines) \
               and all(_a.strip() == _b.strip() for _a, _b in zip(stdout_lines, expected_lines))
    return len(stdout_lines) == len(expected_lines) \
           and all(_a.lower().strip() == _b.lower().strip() for _a, _b in zip(stdout_lines, expected_lines))


def verify_expected(
    stdout_lines: typing.List[str],
    expected_lines: typing.List[str],
    test_result: TestResult,
    case_sensitive: bool = True,
    search: bool = False
):
    """
    Check to lists of strings for quality. Will strip off whitespace from each line
    before checking for equality. The stdout_lines should be from the student code.
    The expected_lines should then be whichever lines are expected for this test.

    * The fields on the test_result object will be set automatically based on if the
    expected output was found. *

    :param stdout_lines: students lines as a list of strings
    :param expected_lines: expected lines as a list of strings
    :param test_result: TestResult object for this test
    :param case_sensitive: boolean to indicate if the comparison should be case sensitive
    :param search: boolean to indicate if the stdout should be searched instead of
                   directly compared for equality
    :return:
    """

    compare_func = search_lines if search else test_lines
    if not compare_func(stdout_lines, expected_lines, case_sensitive=case_sensitive):
        test_result.stdout += 'your lines:\n' + '\n'.join(stdout_lines) + '\n\n' \
                              + 'we expected:\n' + '\n'.join(expected_lines)
        test_result.message = 'Did not receive expected output'
        test_result.passed = False
    else:
        test_result.stdout += 'test passed, we received the expected output'
        test_result.message = 'Expected output found'
        test_result.passed = True


def xv6_run(cmd: str, test_result: TestResult, timeout=5) -> typing.List[str]:
    """
    Start xv6 and run command specified. The test_result.stdout will
    be appended with a message saying what command is being run.

    We return a list of the lines parsed

    :param cmd:
    :param test_result:
    :param timeout:
    :return:
    """
    command = 'timeout {} qemu-system-i386 -serial mon:stdio ' \
              '-drive file=./xv6.img,media=disk,index=0,format=raw ' \
              '-drive file=./fs.img,media=disk,index=1,format=raw ' \
              '-smp 1 -m 512 -display none -nographic'.format(timeout)

    test_result.stdout += 'Running "{}" in xv6\n\n'.format(cmd)

    with open('command', 'w') as f:
        f.write('\n' + cmd + '\n')
    stdout, retcode = exec_as_student(command + ' < command', timeout=timeout+1)
    stdout = stdout.split('\n')

    boot_line = None
    for index, line in enumerate(stdout):
        if line.endswith('xv6...'):
            boot_line = index
            break

    if boot_line is not None:
        stdout = stdout[boot_line:]

    stdout = '\n'.join(stdout)

    return trim(stdout)


def did_xv6_crash(stdout_lines: typing.List[str], test_result: TestResult):
    """
    Will check output to see if xv6 crashed. We look for cpu0: panic, and
    or unexpected traps.

    If a crash is detected, the test_result will be set with and True will
    be returned,

    :param stdout_lines:
    :param test_result:
    :return:
    """
    if any('cpu0: panic' in line for line in stdout_lines):
        test_result.stdout += 'xv6 did not boot\n\n' + '-'*20 \
            + '\nstdout:\n' + '\n'.join(stdout_lines)
        test_result.passed = False
        test_result.message = 'xv6 does not boot!\n'
        return True

    passed = True
    for line in stdout_lines:
        passed = 'unexpected trap' not in line and passed

    if not passed:
        test_result.stdout += 'trap error detected\n\n' + '-'*20 \
            + '\nstdout:\n' + '\n'.join(stdout_lines)
        test_result.passed = False
        test_result.message = 'xv6 does not boot!\n'
        return True

    return False

