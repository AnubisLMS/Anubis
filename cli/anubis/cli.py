"""Console script for anubis."""

import base64
import json
import os
import shutil
import string
import sys
import getpass
import logging
from datetime import datetime, timedelta

import click
import requests
import yaml
API_URL = 'https://anubis.osiris.services/api'
conf_dir = os.path.join(os.environ.get("HOME"), ".anubis")
conf_file = os.path.join(os.environ.get("HOME"), ".anubis/config.json")
assignment_base = None


def prompt_auth():
    username = input('Anubis Username: ')
    password = getpass.getpass('Anubis Password: ')
    return username, password

def load_conf():
    return json.load(open(conf_file))


def set_conf(conf):
    json.dump(conf, open(conf_file, 'w'))


def init_conf():
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir, exist_ok=True)

    if not os.path.isfile(conf_file):
        set_conf({"auth": {"username": None, "password": None}})


def load_auth():
    if not os.path.isfile(conf_file):
        init_conf()

        username, password = prompt_auth()
        set_auth(username, password)

    conf = load_conf()
    return conf['auth']['username'], conf['auth']['password']


def set_auth(username, password):
    conf = load_conf()
    conf['auth']['username'] = username
    conf['auth']['password'] = password
    set_conf(conf)


def post_json(path: str, data: dict, params=None):
    """
    Do a POST request to the API with a json object.

    :return: requests.Response
    """
    if params is None:
        params = {}

    auth = load_auth()
    if auth == (None, None):
        click.echo(click.style('You need to sign in', fg='red'))
        click.echo(click.style('anubis -u username -p password ...', fg='red'))
        exit(0)

    r = requests.post(
        API_URL + path,
        headers={'Content-Type': 'application/json'},
        params=params,
        json=data,
        auth=auth,
    )

    if r.status_code != 200:
        logging.error('status_code: {}'.format(r.status_code))
        logging.error(r.headers)
        logging.error(r.text)
        exit(1)

    return r


def get_json(path: str, params=None):
    """


    :return: requests.Response
    """
    if params is None:
        params = {}

    auth = load_auth()
    if auth == (None, None):
        click.echo(click.style('You need to sign in', fg='red'))
        click.echo(click.style('anubis -u username -p password ...', fg='red'))
        exit(0)

    r = requests.get(
        API_URL + path,
        params=params,
        auth=auth,
    )

    assert r.status_code == 200

    return r


def safe_filename(filename: str) -> str:
    filename = filename.lower().replace(' ', '-')
    allowed = set(string.ascii_letters + string.digits + '_-')
    filename = ''.join(i for i in filename if i in allowed)
    return filename


@click.group()
@click.option('--debug/-d', default=False)
@click.option('--username/-u', default=None)
@click.option('--password/-p', default=None)
def main(debug, username, password):
    global assignment_base
    assignment_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assignment'))

    if debug:
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))
        global API_URL
        API_URL = 'http://localhost:5000'

    if username is not None or password is not None:
        c_username, c_password = load_auth()
        set_auth(username or c_username, password or c_password)

    sys.path.append(os.getcwd())


@main.group()
def assignment():
    pass


@assignment.command()
def sync():
    assignment_meta = yaml.safe_load(open('assignment.yml').read())
    click.echo(json.dumps(assignment_meta, indent=2))
    import assignment
    import utils
    assignment_meta['tests'] = list(utils.registered_tests.keys())
    r = post_json('/private/assignment/sync', assignment_meta)
    click.echo(json.dumps(r.json(), indent=2))


@assignment.command()
@click.argument('assignment-name')
def init(assignment_name):
    safe_assignment_name = safe_filename(assignment_name)

    # Copy files over
    click.echo('Creating assignment directory...')
    sample_base = os.path.join(assignment_base, 'sample_assignment')
    shutil.copytree(
        sample_base,
        safe_assignment_name,
        symlinks=True
    )

    click.echo('Initializing the assignment with sample data...')
    meta_path = os.path.join(safe_assignment_name, 'assignment.yml')
    unique_code = base64.b16encode(os.urandom(4)).decode().lower()
    now = datetime.now()
    week_from_now = now + timedelta(weeks=1)
    meta = open(meta_path).read().format(
        name=os.path.basename(safe_assignment_name),
        code=unique_code,
        now=now.strftime('%F %T'),
        week_from_now=week_from_now.strftime('%F %T')
    )
    with open(meta_path, 'w') as f:
        f.write(meta)
        f.close()

    click.echo()
    click.echo(click.style('You now have an Anubis assignment initialized at ', fg='yellow')
               + click.style(safe_assignment_name, fg='blue'))
    click.echo(click.style('cd into that directory and run the sync command to upload it to Anubis.', fg='yellow'))
    click.echo()
    click.echo(click.style('cd {}'.format(safe_assignment_name), fg='blue'))
    click.echo(click.style('anubis assignment build --push', fg='blue'))
    click.echo(click.style('anubis assignment sync', fg='blue'))


@main.command()
@click.argument('netids', nargs=-1)
def stats(netids):
    params = {}
    if len(netids) > 0:
        params['netids'] = '\n'.join(netids)


@assignment.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--push/-p', default=False)
def build(path, push):
    assignment_meta = yaml.safe_load(open(os.path.join(path, 'assignment.yml')).read())

    # Build base image
    assert os.system('docker build -t {} {}'.format(
        'registry.osiris.services/anubis/assignment-base:latest', assignment_base)) == 0

    # Build assignment image
    assert os.system('docker build -t {} {}'.format(
        assignment_meta['assignment']['pipeline_image'], path)) == 0

    if push:
        assert os.system('docker push {}'.format(
            assignment_meta['assignment']['pipeline_image'])) == 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
