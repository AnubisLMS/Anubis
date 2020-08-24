#!/usr/bin/env python3

import json
import os
import subprocess
import traceback
import typing

import git
import yaml

token = os.environ.get('TOKEN')
commit = os.environ.get('COMMIT')
git_repo = os.environ.get('GIT_REPO')
submission_id = os.environ.get('SUBMISSION_ID')

del os.environ['TOKEN']


def report_error(message: str, traceback: str, fatale: bool):
    print('report_error {}'.format(json.dumps({
        'submission_id': submission_id,
        'token': token,
        'commit': commit,
        'message': message,
        'traceback': traceback,
        'fatale': fatale,
    }, indent=2)))


def report_state(state: str):
    print('report_state {}'.format(json.dumps({
        'submission_id': submission_id,
        'token': token,
        'commit': commit,
        'state': state,
    }, indent=2)))


def report_build_results(stdout: str, passed: bool):
    print('report_build {}'.format(json.dumps({
        'submission_id': submission_id,
        'token': token,
        'commit': commit,
        'stdout': stdout,
        'passed': passed,
    }, indent=2)))


def report_test_results(test_name: str, stdout: str, error: str, passed: bool):
    print('report_test_results {}'.format(json.dumps({
        'submission_id': submission_id,
        'token': token,
        'commit': commit,
        'test_name': test_name,
        'stdout': stdout,
        'error': error,
        'passed': passed,
    }, indent=2)))


def exec_as_student(cmd, timeout=60) -> typing.Tuple[str, bool]:
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


assignment_filename = None
for assignment_filename_option in ['assignment.yml', 'assignment.yaml']:
    if os.path.isfile(assignment_filename_option):
        assignment_filename = assignment_filename_option
        break

if assignment_filename is None:
    report_error('No assignment.yml was found', '', True)
    exit(0)

with open(assignment_filename, 'r') as f:
    try:
        assignment_data = yaml.safe_load(f.read())
    except yaml.YAMLError:
        report_error('Unable to read assignment yaml', traceback.format_exc(), True)

print(assignment_data)

# Clone
git.Git('./student').clone(git_repo)

# build
build_stdout, build_passed = exec_as_student(
    assignment_data['build']['command'],
    timeout=assignment_data['build']['command'] if 'command' in assignment_data['build'] else 60
)
report_build_results(build_stdout, build_passed)
if not build_passed:
    report_error('Build error', '', True)
    exit(0)

# Tests
for test_meta in assignment_data['tests']:
    test_name = test_meta['name']
    test_script = test_meta['script']
    timeout = test_meta['timeout'] if 'timeout' in test_meta else 60

    # TODO run tests
