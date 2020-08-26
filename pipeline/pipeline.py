#!/usr/bin/env python3

import base64
import json
import logging
import os
import traceback

import git
import requests
import yaml

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(logging.StreamHandler())

from utils import fix_permissions, exec_as_student

DEBUG = os.environ.get('DEBUG', default='0') == '1'

if not DEBUG:
    TOKEN = os.environ.get('TOKEN')
    COMMIT = os.environ.get('COMMIT')
    GIT_REPO = os.environ.get('GIT_REPO')
    SUBMISSION_ID = os.environ.get('SUBMISSION_ID')
    del os.environ['TOKEN']
else:
    TOKEN = 'DEBUG'
    COMMIT = 'DEBUG'
    GIT_REPO = 'DEBUG'
    SUBMISSION_ID = 'DEBUG'


def post(path: str, data: dict):
    headers = {'Content-Type': 'application/json'}
    params = {'token': TOKEN}

    # Attempt to contact the pipeline API
    try:
        res = requests.post(
            'http://anubis-pipeline-api:5000' + path,
            headers=headers,
            params=params,
            json=data,
        )
    except:
        logging.error('UNABLE TO REPORT POST TO PIPELINE API')
        exit(0)

    # If the call to the api failed we're in trouble,
    # and need to abort.
    if res.status_code != 200:
        logging.error('UNABLE TO REPORT POST TO PIPELINE API')
        exit(0)

    return res


def report_panic(message: str, traceback: str, ):
    """
    Report and error to the API

    :param message: error message
    :param traceback: optional traceback
    :return:
    """
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        'message': message,
        'traceback': traceback,
    }
    print('report_error {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/panic/{}'.format(SUBMISSION_ID), data)


def report_state(state: str):
    """
    Report a state update for the current submission

    :param state: text representation of state
    :return:
    """
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        'state': state,
    }
    print('report_state {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/state/{}'.format(SUBMISSION_ID), data)


def report_build_results(stdout: str, passed: bool):
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        'stdout': base64.b16encode(stdout).decode(),
        'passed': passed,
    }
    print('report_build {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/build/{}'.format(SUBMISSION_ID), data)


def report_test_results(test_name: str, stdout: str, message: str, passed: bool):
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        'test_name': test_name,
        'stdout': base64.b16encode(stdout).decode(),
        'message': message,
        'passed': passed,
    }
    print('report_test_results {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/test/{}'.format(SUBMISSION_ID), data)


def get_assignment_data() -> dict:
    """
    Load the assignment metadata out from the assignment yaml file

    :return:
    """

    # Figure out filename
    assignment_filename = None
    for assignment_filename_option in ['assignment.yml', 'assignment.yaml']:
        if os.path.isfile(assignment_filename_option):
            assignment_filename = assignment_filename_option
            break

    # Make sure we figured out the metadata filename
    if assignment_filename is None:
        report_panic('No assignment.yml was found', '')
        exit(0)

    # Load yaml
    with open(assignment_filename, 'r') as f:
        try:
            assignment_data = yaml.safe_load(f.read())
        except yaml.YAMLError:
            report_panic('Unable to read assignment yaml', traceback.format_exc())

    logging.info(assignment_data)

    return assignment_data


def clone():
    """
    Clone the assigment repo into the student folder.
    File permissions will need to be updated.

    :return:
    """
    report_state('Cloning repo')
    # Clone
    try:
        repo = git.Repo.clone_from(GIT_REPO, './student')
        repo.git.checkout(COMMIT)
    except git.exc.GitCommandError:
        report_panic('Git error', traceback.format_exc())
        exit(0)

    fix_permissions()
    os.system('rm -rf ./student/.git')


def run_build(assignment_data: dict):
    """
    Build the student repo.


    :param assignment_data: assignment meta
    :return:
    """
    # build
    report_state('Building...')
    build_stdout, build_passed = exec_as_student(
        assignment_data['build']['command'],
        timeout=assignment_data['build']['timeout'] if 'timeout' in assignment_data['build'] else 60
    )
    report_build_results(build_stdout, build_passed)
    if not build_passed:
        exit(0)


def run_tests(assignment_data: dict):
    """
    Run the assignment test scripts. Update submission state as you go.

    :param assignment_data:
    :return:
    """

    try:
        import assignment
    except ImportError:
        report_panic('Unable to import assignment', traceback.format_exc())
        exit(0)

    from utils import registered_tests

    # Tests
    for test_meta in assignment_data['tests']:
        test_name = test_meta['name']

        if test_name not in registered_tests:
            report_panic('Unable to find function for test_name {}'.format(test_name), '')
            exit(0)

        report_state('Running test: '.format(test_name))
        result = registered_tests[test_name]()

        print(result.stdout)

        report_test_results(test_name, result.stdout, result.message, result.passed)

        # TODO run tests


def main():
    assignment_data = get_assignment_data()
    clone()

    os.chdir('./student')
    run_build(assignment_data)
    run_tests(assignment_data)


if __name__ == '__main__':
    main()
