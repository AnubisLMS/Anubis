import subprocess
import typing


class TestResult(object):
    def __init__(self, message: str, passed: bool):
        self.message = message
        self.passed = passed


def exec_as_student(cmd, timeout=60) -> typing.Tuple[str, bool]:
    """


    :param cmd:
    :param timeout:
    :return:
    """
    return_code = 0
    try:
        stdout = subprocess.check_output(
            ["su", "student", "sh -c \"{}\"".format(cmd)],
            stderr=subprocess.STDOUT,
            shell=True,
            timeout=timeout,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.output
        return_code = e.returncode
    return stdout, return_code == 0
