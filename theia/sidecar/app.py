#!/usr/bin/python3

import os
import json
import string
import subprocess

from flask import Flask, Response, request, make_response

app = Flask(__name__)
NETID = os.environ.get('NETID', default=None)
ADMIN = os.environ.get('ANUBIS_ADMIN', default=None) == 'ON'


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
    repo: str = request.form.get('repo', default=None)
    message: str = request.form.get('message', default='Anubis Cloud IDE Autosave').strip()

    # Default commit message if empty
    if message == '':
        message = 'Anubis Cloud IDE Autosave'

    # Add netid to commit message
    if NETID is not None:
        message += ' netid=' + NETID

    # Make sure that the repo given exists and is a git repo
    if repo is None or not os.path.isdir(os.path.join(repo, '.git')):
        return text_response('Please navigate to the repository that you would like to autosave')

    try:
        # Add
        add = subprocess.run(
            ['git', 'add', '.'],
            cwd=repo,
            timeout=3,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if add.returncode != 0:
            return text_response('Failed to git add')

        # Commit
        commit = subprocess.run(
            ['git', 'commit', '--no-verify', '-m', message],
            cwd=repo,
            timeout=3,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if commit.returncode != 0:
            return text_response('Failed to git commit')

        # Push
        push = subprocess.run(
            ['git', 'push', '--no-verify'],
            cwd=repo,
            timeout=3,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if push.returncode != 0:
            return text_response('Failed to git push')

    except subprocess.TimeoutExpired:
        return text_response('Autosave timeout')

    output = (add.stdout + commit.stdout + push.stdout + b'\n').decode()
    return text_response(output)


if ADMIN:
    @app.route('/clone', methods=['POST'])
    def clone():
        assignment_name: str = request.json['assignment_name']
        repos: list = request.json['repos']
        path: str = request.json['path']

        if not path.startswith('/home/anubis/'):
            response = make_response(
                'You can only clone student repos under /home/anubis/\n',
            )
            response.headers = {'Content-Type': 'text/plain'}
            return response

        assignment_name = relatively_safe_filename(assignment_name)

        os.makedirs(os.path.join(path, assignment_name), exist_ok=True)
        path = os.path.join(path, assignment_name)

        succeeded = []
        failed = []

        for repo in repos:
            repo_url: str = repo['url']
            repo_base = repo_url.removeprefix('https://github.com/')
            netid: str = repo['netid']

            r = subprocess.run(
                ['git', 'clone', repo_url, netid],
                cwd=path,
                timeout=5,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if r.returncode != 0:
                failed.append('Failed to clone {} for {}'.format(repo_base, netid))
                print(r.stdout)
                continue

            succeeded.append('{:<12} :: {:<32} -> {}/{}'.format(netid, repo_base, assignment_name, netid))

        return text_response(
            'Succeeded:\n' + '\n'.join(succeeded) + '\nFailed:\n' + '\n'.join(failed)
        )


