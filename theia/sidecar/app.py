#!/usr/bin/python3

from flask import Flask, request, make_response
import subprocess

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    message = request.form.get('message', default='Anubis Cloud IDE Autosave')
    if message.strip() == '':
        message = 'Anubis Cloud IDE Autosave'

    try:
        # Add
        add = subprocess.run(
            ['git', 'add', '.'],
            cwd='/home/project',
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
            ['git', 'commit', '-m', message],
            cwd='/home/project',
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
            ['git', 'push'],
            cwd='/home/project',
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
