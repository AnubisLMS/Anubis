"""Console script for anubis."""

import base64
import getpass
import json
import logging
import os
import shutil
import string
import sys
import typing
from datetime import datetime, timedelta

import click
import requests
import yaml

INCLUSTER = True
API_URL = 'http://anubis-api:5000'
COURSE_ID = os.environ.get('COURSE_ID', None)
COURSE_CODE = os.environ.get('COURSE_CODE', 'CS-UY 3224')
conf_dir = os.path.join(os.environ.get("HOME"), ".anubis")
conf_file = os.path.join(os.environ.get("HOME"), ".anubis/config.json")
assignment_base = None


def prompt_auth_data() -> typing.Dict[str, dict]:
    b64_auth_data = getpass.getpass('Token from anubis: ')

    try:
        decoded_auth_data = base64.b64decode(b64_auth_data.encode()).decode()
    except Exception as e:
        print(e)
        print('Unable to base64 decode token')
        exit(1)

    try:
        auth_data = json.loads(decoded_auth_data)
    except Exception as e:
        print(e)
        print('Unable to json decode token')
        exit(1)

    return auth_data


def get_conf(key, default=None):
    conf = load_conf()
    return conf.get(key, default)


def load_conf():
    return json.load(open(conf_file))


def set_conf(conf):
    json.dump(conf, open(conf_file, 'w'))


def init_conf():
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir, exist_ok=True)

    if not os.path.isfile(conf_file):
        set_conf({
            "url": "http://anubis-api:5000",
            "token": None,
        })


def _make_request(path, request_func, **kwargs):
    if 'params' in kwargs and kwargs['params'] is None:
        kwargs['params'] = {}

    r = request_func(
        API_URL + path,
        headers={'Content-Type': 'application/json'},
        cookies={'token': get_conf('incluster')},
        **kwargs
    )

    if r.status_code != 200:
        logging.error('status_code: {}'.format(r.status_code))
        logging.error(r.headers)
        logging.error(r.text)
        exit(1)

    return r


def post_json(path: str, data: dict, params=None):
    """
    Do a POST request to the API with a json object.

    :return: requests.Response
    """

    return _make_request(path, requests.post, json=data, params=params)


def get_json(path: str, params=None):
    """
    GET something from the api, expecting a json response.

    :return: requests.Response
    """
    return _make_request(path, requests.get, params=params)


def relatively_safe_filename(filename: str) -> str:
    filename = filename.lower().replace(' ', '-')
    allowed = set(string.ascii_letters + string.digits + '_-')
    filename = ''.join(i for i in filename if i in allowed)
    return filename


@click.group()
@click.option('--debug/-d', default=False)
def main(debug):
    global assignment_base
    assignment_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assignment'))

    init_conf()

    if debug:
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))

    sys.path.append(os.getcwd())


@main.group()
def assignment():
    pass

@main.group()
def config():
    pass


@config.command()
def show():
    conf = load_conf()
    click.echo(json.dumps(conf, indent=2))


@main.command()
def whoami():
    r = get_json('/public/auth/whoami')
    click.echo(json.dumps(r.json(), indent=2))


@assignment.command()
def sync():
    if not os.path.exists('meta.yml'):
        click.echo('no meta.yml found!')
        return 1
    assignment_meta = yaml.safe_load(open('meta.yml').read())
    # click.echo(json.dumps(assignment_meta, indent=2))
    try:
        import assignment
        import utils
    except ImportError:
        click.echo('Not in an assignment directory')
        return 1
    assignment_meta['assignment']['tests'] = list(utils.registered_tests.keys())
    r = post_json('/admin/assignments/sync', assignment_meta)
    click.echo(json.dumps(r.json(), indent=2))


@assignment.command()
@click.argument('assignment-name')
def init(assignment_name):
    safe_assignment_name = relatively_safe_filename(assignment_name)

    assignment_base: str = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assignment'))

    # Copy files over
    click.echo('Creating assignment directory...')
    shutil.copytree(
        assignment_base,
        safe_assignment_name,
        symlinks=True
    )

    click.echo('Initializing the assignment with sample data...')
    unique_code = base64.b16encode(os.urandom(4)).decode().lower()
    now = datetime.now()
    week_from_now = now + timedelta(weeks=1)

    # Populate meta
    meta_path = os.path.join(safe_assignment_name, 'meta.yml')
    meta = open(meta_path).read().format(
        name=os.path.basename(safe_assignment_name),
        unique_code=unique_code,
        now=now.strftime('%F %T'),
        week_from_now=week_from_now.strftime('%F %T'),
        course_code=COURSE_CODE,
    )
    with open(meta_path, 'w') as f:
        f.write(meta)
        f.close()

    # Populate test.sh
    test_path = os.path.join(safe_assignment_name, 'test.sh')
    test_sh = open(test_path).read().format(
        unique_code=unique_code,
    )
    with open(test_path, 'w') as f:
        f.write(test_sh)
        f.close()

    click.echo()
    click.echo(click.style('You now have an Anubis assignment initialized at ', fg='yellow')
               + click.style(safe_assignment_name, fg='blue'))
    click.echo(click.style('cd into that directory and run the sync command to upload it to Anubis.', fg='yellow'))
    click.echo()
    click.echo(click.style('cd {}'.format(safe_assignment_name), fg='blue'))
    click.echo(click.style('anubis assignment build --push', fg='blue'))
    click.echo(click.style('anubis assignment sync', fg='blue'))


@assignment.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--push/-p', default=False)
def build(path, push):
    if not os.path.exists('meta.yml'):
        click.echo('no meta.yml found!')
        return 1
    assignment_meta = yaml.safe_load(open(os.path.join(path, 'meta.yml')).read())

    # Build assignment image
    assert os.system('docker build -t {} {}'.format(
        assignment_meta['assignment']['pipeline_image'], path)) == 0

    if push:
        assert os.system('docker push {}'.format(
            assignment_meta['assignment']['pipeline_image'])) == 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
