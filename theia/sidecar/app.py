#!/usr/bin/python3

import os.path
import subprocess

from flask import Flask, request, make_response

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    # Get options from the form
    repo: str = request.form.get('repo', default=None)
    message: str = request.form.get('message', default='Anubis Cloud IDE Autosave').strip()

    # Default commit message if empty
    if message == '':
        message = 'Anubis Cloud IDE Autosave'

    # Make sure that the repo given exists and is a git repo
    if repo is None or not os.path.isdir(os.path.join(repo, '.git')):
        response = make_response(
            'Please navigate to the repository that you would like to autosave\n',
        )
        response.headers = {'Content-Type': 'text/plain'}
        return response

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
            response = make_response(
                'Failed to git add\n',
            )
            response.headers = {'Content-Type': 'text/plain'}
            return response

        # Commit
        commit = subprocess.run(
            ['git', 'commit', '--no-verify', '-m', message],
            cwd=repo,
            timeout=3,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if commit.returncode != 0:
            response = make_response(
                'Failed to git commit\n',
            )
            response.headers = {'Content-Type': 'text/plain'}
            return response

        # Push
        push = subprocess.run(
            ['git', 'push', '--no-verify'],
            cwd=repo,
            timeout=3,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if push.returncode != 0:
            response = make_response(
                'Failed to git push\n',
            )
            response.headers = {'Content-Type': 'text/plain'}
            return response

    except subprocess.TimeoutExpired:
        response = make_response(
            'Autosave timeout\n',
        )
        response.headers = {'Content-Type': 'text/plain'}
        return response

    output = (add.stdout + commit.stdout + push.stdout + b'\n').decode()
    response = make_response(output)
    response.headers = {'Content-Type': 'text/plain'}
    return response
