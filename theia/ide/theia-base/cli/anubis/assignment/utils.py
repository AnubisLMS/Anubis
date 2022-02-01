import collections
import difflib
import functools
import json
import logging
import os
import subprocess
import typing
import warnings

registered_tests: typing.Dict[str, typing.Callable[[], "TestResult"]] = {}
build_function = None

CompareFuncReturnT = typing.Tuple[bool, typing.List[str]]
CompareFuncT = typing.Callable[[typing.List[str], typing.List[str], bool], CompareFuncReturnT]


class TestResult(object):
    def __init__(self):
        self.output_type = 'text'
        self.output = ""
        self.message = ""
        self.passed = True

    def __repr__(self):
        return "<TestResult\n  passed={}\n  message='{:5.5}'\n  output_type='{}'\n  output='{:5.5}'\n>".format(
            self.passed,
            self.message,
            self.output_type,
            self.output,
        )


class BuildResult(object):
    def __init__(self):
        self.stdout = ""
        self.passed = True

    def __repr__(self):
        return "<BuildResult\n  passed={}\n  stdout='{:5.5}'>".format(
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

        if wrapper.__dict__.get('test', None) is None:
            wrapper.test = {}

        wrapper.test['name'] = test_name
        if 'hidden' not in wrapper.test:
            wrapper.test['hidden'] = False
        if 'points' not in wrapper.test:
            wrapper.test['points'] = 10

        registered_tests[test_name] = wrapper

        return wrapper

    return decorator


def hide_test():
    def decorator(func):
        if func.__dict__.get('test', None) is None:
            func.test = {}
        func.test['hidden'] = True

        return func

    return decorator


def points_test(points: int):
    def decorator(func):
        if func.__dict__.get('test', None) is None:
            func.test = {}
        func.test['points'] = points

        return func

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
        stdout_lines = stdout_lines[stdout_lines.index('init: starting sh') + 1:]
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
) -> CompareFuncReturnT:
    """
    Search lines for expected lines. This will return true if all expected lines are in the
    student standard out lines in order. There can be interruptions in the student standard out.
    This function has the advantage of allowing students to still print out debugging lines
    while their output is still accurately checked for  the expected result. The diff is not
    available for this.

    >>> search_lines(['a', 'b', 'c'], ['a', 'b', 'c']) -> (True, [])
    >>> search_lines(['a', 'debugging', 'b', 'c'], ['a', 'b', 'c']) -> (True, [])
    >>> search_lines(['a', 'b'],      ['a', 'b', 'c']) -> (False, [])

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
        return False, []
    return list(sorted(found)) == found, []


def test_lines(
    stdout_lines: typing.List[str],
    expected_lines: typing.List[str],
    case_sensitive: bool = True,
    context_length: int = 1000,
) -> CompareFuncReturnT:
    """
    Test lines for exact equality. Whitespace will be stripped off each line automatically.

    * Optionally specify if the equality comparison should be case sensitive *

    >>> test_lines(['a', 'b', 'c'], ['a', 'b', 'c']) -> (True, [])
    >>> test_lines(['a', 'debugging', 'b', 'c'], ['a', 'b', 'c'])
    # -> (False, ['--- ', '+++ ', '@@ -1,3 +1,4 @@', ' a', '+debugging', ' b', ' c'])
    >>> test_lines(['a', 'b'],      ['a', 'b', 'c'])
    # -> (False, ['--- ', '+++ ', '@@ -1,3 +1,2 @@', ' a', ' b', '-c'])

    :param stdout_lines: students standard out lines as a list of strings
    :param expected_lines: expected lines as a list of strings
    :param case_sensitive: optional boolean to indicate if comparison should be case sensitive
    :param context_length: the length of the context of the generated diff (the smaller the faster)
    :return: True and an empty list if exact match was found, False with the unified diff otherwise
    """
    # A rolling deque containing the lines of context of the diff that occurs (if any)
    context = collections.deque(maxlen=context_length)
    # Record the first occurence of a mismatch
    mismatch_index = -1
    # The remaining offset until the first occurence of mismatch is centralized
    # within the context
    context_remaining_offset = context_length // 2
    # A general preprocessor function for text
    if case_sensitive:
        preprocess_func = lambda *texts: tuple(text.strip() for text in texts)
    else:
        preprocess_func = lambda *texts: tuple(text.strip().lower() for text in texts)

    for index, (_a, _b) in enumerate(zip(expected_lines, stdout_lines)):
        # We defer text preprocessing until we need the lines
        _a, _b = preprocess_func(_a, _b)
        context.append((_a, _b))

        # When there is a mismatch already, we are only motivated to fill up
        # the appropriate context lines
        if mismatch_index != -1:
            # Break when the context is full and the mismatched line is
            # centralized
            if len(context) == context_length and context_remaining_offset <= 0:
                break
            # Continue until we fill up the context
            context_remaining_offset -= 1
            continue
        elif _a != _b:
            mismatch_index = index

    # unzip the context as tuples
    expected_context, stdout_context = zip(*context) if len(context) > 0 else (tuple(), tuple())

    # We fill the context with the leading part of the lines that
    # only present in the longer list of lines
    # if there IS a mismatch (i.e. mismatch_index != -1 or len(expected_lines) != len(stdout_lines))
    start = min(len(expected_lines), len(stdout_lines))

    if mismatch_index == -1:
        if len(expected_lines) == len(stdout_lines):
            return True, []

        # If no mismatch occurs, we fill the entire trailing part of
        # the longer list into the context 
        end = start + context_length
    else:
        # Otherwise, we only fill the context to the desired size 
        end = start + (context_length - len(context))

    if len(expected_lines) > len(stdout_lines):
        expected_context += preprocess_func(*expected_lines[start:end])
    else:
        stdout_context += preprocess_func(*stdout_lines[start:end])

    return False, list(difflib.unified_diff(expected_context, stdout_context, lineterm=""))


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

    compare_func: CompareFuncT = search_lines if search else test_lines
    passed, diff = compare_func(stdout_lines, expected_lines, case_sensitive=case_sensitive)
    if not passed:
        if diff:
            test_result.output_type = 'diff'
            test_result.output = '\n'.join(diff)
        else:
            # If diff is not available, fall back to the old way of displaying outputs
            test_result.output_type = 'text'
            test_result.output += 'your lines:\n' + '\n'.join(stdout_lines) + '\n\n' \
                                  + 'we expected:\n' + '\n'.join(expected_lines)
        test_result.message = 'Did not receive expected output'
        test_result.passed = False
    else:
        test_result.output_type = 'text'
        test_result.output += 'test passed, we received the expected output'
        test_result.message = 'Expected output found'
        test_result.passed = True


def xv6_run(cmd: str, test_result: TestResult, timeout=5) -> typing.List[str]:
    """
    Start xv6 and run command specified. The test_result.output will
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

    test_result.output += 'Running "{}" in xv6\n\n'.format(cmd)

    with open('command', 'w') as f:
        f.write('\n' + cmd + '\n')
    stdout, retcode = exec_as_student(command + ' < command', timeout=timeout + 1)
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
        test_result.output_type = 'text'
        test_result.output += 'xv6 did not boot\n\n' + '-' * 20 \
                              + '\nstdout:\n' + '\n'.join(stdout_lines)
        test_result.passed = False
        test_result.message = 'xv6 does not boot!\n'
        return True

    passed = True
    for line in stdout_lines:
        passed = 'unexpected trap' not in line and passed

    if not passed:
        test_result.output_type = 'text'
        test_result.output += 'trap error detected\n\n' + '-' * 20 \
                              + '\nstdout:\n' + '\n'.join(stdout_lines)
        test_result.passed = False
        test_result.message = 'xv6 does not boot!\n'
        return True

    return False
