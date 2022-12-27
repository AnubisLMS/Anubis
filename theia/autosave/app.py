#!/usr/bin/python3

import os
import string
import subprocess
import traceback
import multiprocessing.pool
import typing

from flask import Flask, Response, request, make_response

NETID = os.environ.get('NETID', default=None)
ADMIN = os.environ.get('ANUBIS_ADMIN', default=None) == 'ON'
GIT_REPO = os.environ.get('GIT_REPO', default='')
GIT_REPO_PATH = '/home/anubis/' + GIT_REPO.split('/')[-1]
print(f'GIT_REPO = {GIT_REPO}')
print(f'GIT_REPO_PATH = {GIT_REPO_PATH}')

app = Flask(__name__)


def text_response(message: str, status_code: int = 200) -> Response:
    r = make_response(message + '\n')
    r.status_code = status_code
    r.headers['Content-Type'] = 'application/json'
    return r


def relatively_safe_filename(filename: str) -> str:
    valid_charset = set(string.ascii_letters + string.digits + '_')
    filename = filename.replace(' ', '_').replace('-', '_').lower()
    filename = ''.join(i for i in filename if i in valid_charset)
    return filename


@app.route('/', methods=['POST'])
def index():
    # Get options from the form
    message: str = request.form.get('message', default='Anubis Cloud IDE Autosave').strip()
    push_only: bool = request.form.get('push_only', default='false').lower() == 'true'
    force_push: bool = request.form.get('force_push', default='false').lower() == 'true'

    # Default commit message if empty
    if message == '':
        message = 'Anubis Cloud IDE Autosave'

    # Add netid to commit message
    if NETID is not None:
        message += ' netid=' + NETID

    # Make sure that the repo given exists and is a git repo
    if GIT_REPO_PATH is None or not os.path.isdir(os.path.join(GIT_REPO_PATH, '.git')):
        return text_response('Please navigate to the repository that you would like to autosave')

    output: str = ""

    try:
        # We skip the add and commit phase if push_only is enabled
        # In that case, we will only try to push
        if not push_only:
            # Add
            add = subprocess.run(
                ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'alias.push=push', 'add', '.'],
                cwd=GIT_REPO_PATH,
                timeout=3,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if add.returncode != 0:
                return text_response('Failed to git add')
            output += add.stdout.decode() + '\n'

            # Commit
            commit = subprocess.run(
                ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'alias.commit=commit', 'commit', '--no-verify', '-m',
                 message],
                cwd=GIT_REPO_PATH,
                timeout=3,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if commit.returncode != 0:
                return text_response('Failed to git commit')
            output += commit.stdout.decode() + '\n'

        # Push
        push_args = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'alias.push=push', 'push', '--no-verify', GIT_REPO]
        if force_push:
            push_args.append('--force')
        push = subprocess.run(
            push_args,
            cwd=GIT_REPO_PATH,
            timeout=3,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if push.returncode != 0:
            return text_response('Failed to git push')
        output += push.stdout.decode() + '\n'

    except subprocess.TimeoutExpired:
        return text_response('Autosave timeout')

    return text_response(output)


if ADMIN:

    def _clone_repo(path: str, assignment_name: str, repo: dict) -> typing.Tuple[bool, str]:
        repo_url: str = repo['url']
        repo_base = repo_url.removeprefix('https://github.com/')
        netid: str = repo['netid']

        try:
            r = subprocess.run(
                ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'alias.clone=clone', 'clone', repo_url, netid],
                cwd=path,
                timeout=5,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if r.returncode != 0:
                print(r.stdout)
                return False, 'Failed to clone {} for {}'.format(repo_base, netid)
        except subprocess.TimeoutExpired:
            print(traceback.format_exc())
            return False, 'Failed to clone {} for {} Timeout'.format(repo_base, netid)
        return True, '{:<12} :: {:<32} -> {}/{}'.format(netid, repo_base, assignment_name, netid)


    @app.route('/clone', methods=['POST'])
    def clone():
        assignment_name: str = request.json['assignment_name']
        repos: list = request.json['repos']
        netids: list[str] = request.json['netids']
        path: str = '/home/anubis/'

        assignment_name = relatively_safe_filename(assignment_name)

        os.makedirs(os.path.join(path, assignment_name), exist_ok=True)
        path = os.path.join(path, assignment_name)

        if len(netids) > 0:
            repos = [repo for repo in repos if repo['netid'] in set(netids)]

        with multiprocessing.pool.Pool(8) as pool:
            r = pool.starmap(_clone_repo, [
                (path, assignment_name, repo) for repo in repos
            ])

        succeeded = [message for success, message in r if success is True]
        failed = [message for success, message in r if success is False]

        return text_response(
            'Succeeded:\n' + '\n'.join(succeeded) + '\nFailed:\n' + '\n'.join(failed)
        )
