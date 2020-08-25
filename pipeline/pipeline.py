#!/usr/bin/env python3

import json
import os
import traceback

import utils

import git
import yaml
import requests

token = os.environ.get('TOKEN')
commit = os.environ.get('COMMIT')
git_repo = os.environ.get('GIT_REPO')
submission_id = os.environ.get('SUBMISSION_ID')

del os.environ['TOKEN']


def fix_permissions():
    """
    Fix the file permissions of the student repo

    :return:
    """
    # Update file permissions
    os.system('chown anubis:student -R ./student')
    os.system('rm -rf ./student/.git')


def post(path: str, data: dict):
    res = requests.post('http://anubis-pipeline-api:5000/')


def report_panic(message: str, traceback: str,):
    """
    Report and error to the API

    :param message: error message
    :param traceback: optional traceback
    :param fatale: boolean to indicate if the error was fatale
    :return:
    """
    print('report_error {}'.format(json.dumps({
        'submission_id': submission_id,
        'token': token,
        'commit': commit,
        'message': message,
        'traceback': traceback,
    }, indent=2)))


def report_state(state: str):
    """
    Report a state update for the current submission

    :param state: text representation of state
    :return:
    """
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


def report_test_results(test_name: str, stdout: str, message: str, passed: bool):
    print('report_test_results {}'.format(json.dumps({
        'submission_id': submission_id,
        'token': token,
        'commit': commit,
        'test_name': test_name,
        'stdout': stdout,
        'message': message,
        'passed': passed,
    }, indent=2)))


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
        report_panic('No assignment.yml was found', '', True)
        exit(0)

    # Load yaml
    with open(assignment_filename, 'r') as f:
        try:
            assignment_data = yaml.safe_load(f.read())
        except yaml.YAMLError:
            report_panic('Unable to read assignment yaml', traceback.format_exc(), True)

    print(assignment_data)

    return assignment_data


def clone():
    """
    Clone the assigment repo into the student folder.
    File permissions will need to be updated.

    :return:
    """
    # Clone
    try:
        repo = git.Repo.clone_from(git_repo, './student')
        repo.git.checkout(commit)
    except git.exc.GitCommandError:
        report_panic('Git error', traceback.format_exc())
        exit(0)

    fix_permissions()


def run_build(assignment_data: dict):
    """
    Build the student repo.


    :param assignment_data: assignment meta
    :return:
    """
    # build
    report_state('Building...')
    build_stdout, build_passed = utils.exec_as_student(
        assignment_data['build']['command'],
        timeout=assignment_data['build']['command'] if 'command' in assignment_data['build'] else 60
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
    # Tests
    for test_meta in assignment_data['tests']:
        test_name = test_meta['name']
        test_script = test_meta['script']
        timeout = test_meta['timeout'] if 'timeout' in test_meta else 60

        report_state('Running test: '.format(test_name))

        # TODO run tests


def main():
    assignment_data = get_assignment_data()
    clone()
    run_build(assignment_data)
    run_tests(assignment_data)


if __name__ == '__main__':
    main()