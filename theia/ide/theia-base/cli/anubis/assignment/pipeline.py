#!/usr/bin/env python3

import json
import logging
import os
import traceback

import git
import requests
import yaml
import argparse

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(logging.StreamHandler())


def post(path: str, data: dict, params=None):
    if params is None:
        params = {}
    headers = {'Content-Type': 'application/json'}
    params['token'] = TOKEN

    if DEBUG:
        logging.info("post: {} data: {}".format(path, data))
        return None

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
    print(traceback)
    logging.info('report_error {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/panic/{}'.format(SUBMISSION_ID), data)


try:
    import assignment
except ImportError:
    report_panic('Unable to import assignment', traceback.format_exc())
    exit(0)

from utils import registered_tests, build_function
from utils import Panic

git_creds = os.environ.get('GIT_CRED', default=None)
if git_creds is not None:
    del os.environ['GIT_CRED']
    with open(os.environ.get('HOME') + '/.git-credentials', 'w') as f:
        f.write(git_creds)
        f.close()
    with open(os.environ.get('HOME') + '/.gitconfig', 'w') as f:
        f.write('[credential]\n')
        f.write('\thelper = store\n')
        f.close()

TOKEN = os.environ.get('TOKEN')
DEBUG = False
COMMIT = None
GIT_REPO = None
SUBMISSION_ID = None
del os.environ['TOKEN']


def report_state(state: str, params=None):
    """
    Report a state update for the current submission

    :param params:
    :param state: text representation of state
    :return:
    """
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        'state': state,
    }
    logging.info('report_state {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/state/{}'.format(SUBMISSION_ID), data, params=params)


def report_build_results(stdout: str, passed: bool):
    """
    Report the results of a given build.

    :param stdout:
    :param passed:
    :return:
    """
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        # 'stdout': base64.b16encode(stdout).decode(),
        'stdout': stdout,
        'passed': passed,
    }
    logging.info('report_build {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/build/{}'.format(SUBMISSION_ID), data)


def report_test_results(test_name: str, output_type: str, output: str, message: str, passed: bool):
    """
    Report a single test result to the pipeline API.

    :param test_name:
    :param output_type:
    :param output:
    :param message:
    :param passed:
    :return:
    """
    data = {
        'token': TOKEN,
        'commit': COMMIT,
        'test_name': test_name,
        'output_type': output_type,
        'output': output,
        'message': message,
        'passed': passed,
    }
    logging.info('report_test_results {}'.format(json.dumps(data, indent=2)))
    post('/pipeline/report/test/{}'.format(SUBMISSION_ID), data)


def get_assignment_data() -> dict:
    """
    Load the assignment metadata out from the assignment yaml file

    :return:
    """

    # Figure out filename
    assignment_filename = None
    for assignment_filename_option in ['meta.yml', 'meta.yaml']:
        if os.path.isfile(assignment_filename_option):
            assignment_filename = assignment_filename_option
            break

    # Make sure we figured out the metadata filename
    if assignment_filename is None:
        report_panic('No meta.yml was found', '')
        exit(0)

    # Load yaml
    with open(assignment_filename, 'r') as f:
        try:
            assignment_data = yaml.safe_load(f.read())
        except yaml.YAMLError:
            report_panic('Unable to read assignment yaml', traceback.format_exc())

    logging.info(assignment_data)

    return assignment_data


def clone(args: argparse.Namespace):
    """
    Clone the assigment repo into the student folder.
    File permissions will need to be updated.

    :return:
    """
    report_state('Cloning repo')
    # Clone
    try:
        repo = git.Repo.clone_from(GIT_REPO, args.path)
        if COMMIT.lower() != 'null':
            repo.git.checkout(COMMIT)
    except git.exc.GitCommandError:
        report_panic('Git error', traceback.format_exc())
        exit(0)

    if args.prod:
        os.system(f'rm -rf {args.path}/.git')
        os.system('rm -rf /home/anubis/.git-credentials')
        os.system('rm -rf /home/anubis/.gitconfig')


def run_build():
    """
    Build the student repo.

    :return:
    """
    # build
    report_state('Running Build...')
    result = build_function()
    report_build_results(result.stdout, result.passed)
    if not result.passed:
        exit(0)


def run_tests():
    """
    Run the assignment test scripts. Update submission state as you go.

    :param assignment_data:
    :return:
    """

    # Tests
    for test_name in registered_tests:
        report_state('Running test: {}'.format(test_name))
        result = registered_tests[test_name]()

        report_test_results(test_name, result.output_type, result.output, result.message, result.passed)


def main():
    args = parse_args()
    global COMMIT, GIT_REPO, SUBMISSION_ID, DEBUG
    COMMIT = args.commit
    GIT_REPO = args.git_repo
    SUBMISSION_ID = args.submission_id
    DEBUG = not args.prod
    try:
        # assignment_data = get_assignment_data()
        if args.repo:
            clone(args)
        os.chdir(args.path)

        run_build()
        run_tests()
        report_state('Finished!', params={'processed': '1'})
    except Panic as e:
        report_panic(repr(e), traceback.format_exc())
    except Exception as e:
        report_panic(repr(e), traceback.format_exc())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--prod', dest='prod', action='store_true', help='turn on debug')
    parser.add_argument('--netid', dest='netid', default=None, help='netid of student (only needed in prod)')
    parser.add_argument('--commit', dest='commit', default=None, help='commit from repo to use (only needed in prod)')
    parser.add_argument('--submission-id', dest='submission_id', default=None,
                        help='commit from repo to use (only needed in prod)')
    parser.add_argument('--repo', dest='repo', default=None, help='repo url to clone')
    parser.add_argument('--path', default='.', help='path to student repo')
    return parser.parse_args()


if __name__ == '__main__':
    main()
