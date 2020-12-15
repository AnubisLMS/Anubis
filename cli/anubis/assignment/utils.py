import subprocess
import functools
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
    :return:
    """

    if os.getcwd() == '/home/anubis':
        os.chdir('./student')

    return_code = 0
    try:
        print('{} {}'.format(os.getcwd(), ["env", "-i", "su", "student", "-c", cmd]))
        stdout = subprocess.check_output(
            ["env", "-i", "su", "student", "-c", cmd],
            timeout=timeout,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.output
        return_code = e.returncode

    logging.info('exec_as_student command={} return_code={} stdout={}'.format(
        cmd, return_code, stdout
    ))
    fix_permissions()
    return stdout, return_code


def fix_permissions():
    """
    Fix the file permissions of the student repo

    :return:
    """
    # Update file permissions
    if os.getcwd() == '/root/anubis':
        os.system('chown student:student -R ./student')
    elif os.getcwd() == '/root/anubis/student':
        os.system('chown student:student -R .')
    else:
        print('PANIC I DONT KNOW WHERE I AM')
        exit(0)


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


def trim(stdout: str):
    stdout = stdout.split('\n')
    try:
        stdout = stdout[stdout.index('init: starting sh')+1:]
    except ValueError or IndexError:
        return stdout

    while len(stdout) != 0 and (len(stdout[-1].strip()) == 0 or stdout[-1].strip() == '$'):
        stdout.pop()

    if len(stdout) != 0 and stdout[-1].endswith('$'):
        stdout[-1] = stdout[-1].rstrip('$')

    if len(stdout) != 0 and stdout[0].startswith('$'):
        stdout[0] = stdout[0].lstrip('$').strip()

    for index in range(len(stdout)):
        stdout[index] = stdout[index].strip()

    if len(stdout) != 0 and 'terminating on signal 15' in stdout[-1]:
        stdout.pop()

    if len(stdout) != 0:
        stdout[-1] = stdout[-1].strip('$')

    print(json.dumps(stdout, indent=2))
    return stdout


def verify_expected(stdout, expected):
    def test_lines(lines, _expected):
        return len(lines) == len(_expected) \
               and all(l.strip() == e.strip() for l, e in zip(lines, _expected))

    if not test_lines(stdout, expected):
        return (
            'your lines:\n' + '\n'.join(stdout) + '\n\nwe expected:\n' + '\n'.join(expected),
            'Did not recieve exepected output',
            False
        )
    else:
        return (
            'test passed, we recieved the expected output',
            'Expected output found',
            True
        )


def xv6_run(cmd):
    command = 'timeout 5 qemu-system-i386 -serial mon:stdio ' \
              '-drive file=./xv6.img,media=disk,index=0,format=raw ' \
              '-drive file=./fs.img,media=disk,index=1,format=raw ' \
              '-smp 1 -m 512 -display none -nographic'

    with open('command', 'w') as f:
        f.write('\n' + cmd + '\n')
    stdout, retcode = exec_as_student(command + ' < command')
    stdout = stdout.decode()
    stdout = stdout.split('\n')

    boot_line = None
    for index, line in enumerate(stdout):
        if line.endswith('xv6...'):
            boot_line = index
            break

    if boot_line is not None:
        stdout = stdout[boot_line:]

    stdout = '\n'.join(stdout)

    return trim(stdout), retcode

