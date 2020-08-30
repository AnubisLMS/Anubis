import os
import subprocess
import typing
import logging
import functools

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


def exec_as_student(cmd, timeout=60) -> typing.Tuple[str, bool]:
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
        print('{} {}'.format(os.getcwd(), ["su", "student", "-c", cmd]))
        stdout = subprocess.check_output(
            ["su", "student", "-c", cmd],
            timeout=timeout,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.output
        return_code = e.returncode

    logging.info('exec_as_student command={} return_code={} stdout={}'.format(
        cmd, return_code, stdout
    ))
    fix_permissions()
    return stdout, return_code == 0


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
