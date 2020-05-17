import getpass
import json
import os

import requests
import urllib3


def get_session(args):
    """
    Create and initalize requests.Session based on parsed arguments.

    :args: parsed ArgumentParser object
    """
    s = requests.Session()
    s.headers.update({'Content-Type': 'application/json'})
    if args.debug:
        s.verify = False
        urllib3.disable_warnings()
    home = os.environ.get('HOME', '')

    if os.path.exists(os.path.join(home, '.anubis', 'creds.json')):
        creds = json.load(open(os.path.join(home, '.anubis', 'creds.json')))
        args.auth_username = creds['username']
        args.auth_password = creds['password']

    username = input('enter username: ') if not args.auth_username else args.auth_username
    password = getpass.getpass('enter password: ') if not args.auth_password else args.auth_password

    os.makedirs(os.path.join(home, '.anubis'), exist_ok=True)
    json.dump({'username': username, 'password': password}, open(os.path.join(home, '.anubis', 'creds.json'), 'w'))

    s.auth = (username, password,)
    s.url = 'https://api.nyu.cool' if not args.debug else 'https://api.localhost'
    return s
