"""Console script for anubis."""

import subprocess
import functools
import getpass
import logging
import shutil
import string
import base64
import typing
import json
import glob
import git
import sys
import os
from datetime import datetime, timedelta

import requests
import click
import yaml

INCLUSTER = True
API_URL = 'http://anubis-api:5000'
ANUBIS_ADMIN = os.environ.get('ANUBIS_ADMIN', 'OFF') == 'ON'
ANUBIS_ASSIGNMENT_NAME = os.environ.get('ANUBIS_ASSIGNMENT_NAME', None)
ANUBIS_ASSIGNMENT_TESTS_REPO = os.environ.get('ANUBIS_ASSIGNMENT_TESTS_REPO', None)
COURSE_ID = os.environ.get('COURSE_ID', None)
COURSE_CODE = os.environ.get('COURSE_CODE', 'CS-UY 3224')
conf_dir = os.path.join(os.environ.get("HOME"), ".anubis")
conf_file = os.path.join(os.environ.get("HOME"), ".anubis/config.json")
assignment_base = None


def require_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not ANUBIS_ADMIN:
            click.echo('This command requires an IDE with Admin permissions.', err=True)
            click.echo('If you are a TA and are seeing this message '
                       'check with your professor that you have TA permissions on Anubis.', err=True)
            return 1
        return func(*args, **kwargs)
    return wrapper


def require_not_in_repo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            git.Repo()
            click.echo('This command cannot be run in a git repo. '
                       'Please cd to somewhere else and try again.', err=True)
            return 2
        except git.exc.InvalidGitRepositoryError:
            pass
        return func(*args, **kwargs)
    return wrapper


def require_in_repo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            git.Repo()
            return func(*args, **kwargs)
        except git.exc.InvalidGitRepositoryError:
            click.echo('This command can only be run in a git repo. '
                       'Please cd to the repo you would like to operate on.', err=True)
            return 2
    return wrapper


def shell(cmd: str) -> str:
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE)
    return out.decode()


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


def _make_request(path, request_func, **kwargs) -> requests.Response:
    if 'params' in kwargs and kwargs['params'] is None:
        kwargs['params'] = {}

    r = request_func(
        API_URL + path,
        headers={'Content-Type': 'application/json'},
        cookies={'token': get_conf('incluster'), 'course': get_conf('course_context')},
        **kwargs
    )

    if r.status_code != 200:
        logging.error('status_code: {}'.format(r.status_code))
        logging.error(r.headers)
        logging.error(r.text)
        exit(1)

    return r


def post_json(path: str, data: dict, params=None) -> requests.Response:
    """
    Do a POST request to the API with a json object.

    :return: requests.Response
    """

    return _make_request(path, requests.post, json=data, params=params)


def get_json(path: str, params=None) -> requests.Response:
    """
    GET something from the api, expecting a json response.

    :return: requests.Response
    """
    return _make_request(path, requests.get, params=params)


def relatively_safe_filename(filename: str) -> str:
    valid_charset = set(string.ascii_letters + string.digits + '_')
    filename = filename.replace(' ', '_').replace('-', '_').lower()
    filename = ''.join(i for i in filename if i in valid_charset)
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


@main.command()
@click.argument('message', nargs=-1)
@require_in_repo
def autosave(message):
    repo_root = shell('git rev-parse --show-toplevel').strip()
    if 'fatal: not a git repository' in repo_root:
        click.echo('You are not in a git repo! Please navigate to one to save something!')
        return 1

    status = shell('git status').strip()
    if 'nothing to commit' in status:
        click.echo('Nothing to autosave just yet. Make a change you would like to save!')
        return 2

    r = requests.post('http://localhost:5001/', data={
        'repo': repo_root,
        'message': ' '.join(message),
    })
    click.echo(r.text)


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
@require_admin
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
    assignment_meta['assignment']['tests'] = [test.test for test in utils.registered_tests.values()]
    r = post_json('/admin/assignments/sync', assignment_meta)
    click.echo(json.dumps(r.json(), indent=2))


@assignment.command()
@click.argument('assignment-name')
@require_admin
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
@require_admin
def build(path, push):
    if not os.path.exists('meta.yml'):
        click.echo('No meta.yml found!', err=True)
        return 1
    assignment_meta = yaml.safe_load(open(os.path.join(path, 'meta.yml')).read())

    # Build assignment image
    assert os.system('docker build -t {} {}'.format(
        assignment_meta['assignment']['pipeline_image'], path)) == 0

    if push:
        assert os.system('docker push {}'.format(
            assignment_meta['assignment']['pipeline_image'])) == 0


@assignment.command()
@require_admin
def ls():
    assignments = get_json('/admin/assignments/list').json()['data'].get('assignments', [])
    click.echo(json.dumps(assignments, indent=2))


@assignment.command()
@click.option('--assignment-name', default=ANUBIS_ASSIGNMENT_NAME)
@require_admin
@require_not_in_repo
def clone(assignment_name):
    assignments = get_json('/admin/assignments/list').json()['data'].get('assignments', [])

    for assignment_ in assignments:
        if assignment_.get('name', None) == assignment_name:
            assignment_id = assignment_['id']
            break
    else:
        click.echo('Unable to find an assignment with that name.')
        click.echo('List assignments with:')
        click.echo('  $ anubis assignment ls')
        return 1

    repos = get_json('/admin/assignments/repos/{}'.format(assignment_id)).json()['data'].get('repos', [])

    assignment_path = os.path.join(os.getcwd(), relatively_safe_filename(assignment_name))
    os.makedirs(assignment_path, exist_ok=True)

    click.echo('1/4 Cleaning existing files in destination path...')
    for item in os.listdir(assignment_path):
        to_del = os.path.join(assignment_path, item)
        if os.path.isdir(to_del):
            shutil.rmtree(os.path.join(assignment_path, item))
        else:
            os.remove(to_del)

    click.echo('2/4 Writing manifest')
    manifest_path = os.path.join(assignment_path, 'manifest.json')
    with open(manifest_path, 'w') as manifest_json:
        json.dump({
            'assignment': {
                'name': assignment_name,
                'path': assignment_path,
                'tests': os.path.join(assignment_path, 'assignment_tests'),
            },
            'course': {'code': COURSE_CODE},
            'repos': repos,
        }, manifest_json, indent=2)

    if ANUBIS_ASSIGNMENT_TESTS_REPO is not None:
        repos.append({'url': ANUBIS_ASSIGNMENT_TESTS_REPO, 'netid': 'assignment_tests'})

    click.echo('3/4 Sending clone commands to sidecar... (this may take a bit)')
    r = requests.post('http://localhost:5001/clone', json={
        'assignment_name': assignment_name,
        'path': os.getcwd() + '/',
        'repos': repos,
    }, timeout=30)
    click.echo(r.text)

    click.echo('4/4 Finished!')

    return r.status_code == 200


@assignment.command()
@click.option('--path', default='.', type=click.Path(exists=True), help='Path to repo to test')
@click.option('--manifest', default=None, type=click.Path(), help='Manifest generated from clone')
@click.option('--tests', default=None, type=click.Path(), help='Assignment tests')
@require_admin
@require_in_repo
def test(path: str, manifest: str, tests: str):
    click.echo(f'Entering {path}')
    os.chdir(path)

    click.echo('Searching for manifest')
    if manifest is None:
        manifest = os.path.join(os.getcwd(), '../manifest.json')
    if not os.path.exists(manifest):
        click.echo('Manifest file does not exist. '
                   'Please clone student repo using the anubis assignment clone command.',
                   err=True)
        return 1
    manifest_data = json.load(open(manifest, 'r'))
    assignment_name = manifest_data['assignment']['name']
    course_code = manifest_data['course']['code']
    click.echo(f'Detected assignment :: {course_code} :: {assignment_name}')

    click.echo('Searching for assignment tests')
    if tests is None:
        tests = manifest_data['assignment']['tests']
    if not os.path.isdir(tests):
        click.echo('Assignment tests could not be found. '
                   'Please clone student repo using the anubis assignment clone command.',
                   err=True)
        return 2
    for meta_yaml_path in glob.glob(tests + '/**/meta.yml', recursive=True):
        click.echo(f'Seaching meta: {meta_yaml_path}')
        meta_yaml = yaml.safe_load(open(meta_yaml_path))
        if meta_yaml['assignment']['name'] == assignment_name and meta_yaml['assignment']['class'] == course_code:
            click.echo('Found assignment tests for this assignment')
            tests_root = os.path.dirname(meta_yaml_path)
            break
    else:
        click.echo('Unable to find assignment tests for this assignment. '
                   'Please clone student repo using the anubis assignment clone command.',
                   err=True)
        return 3

    click.echo('Running assignment test')
    r = subprocess.run([
        '/usr/bin/python3',
        os.path.join(tests_root, 'pipeline.py'),
        f'--verbose',
        f'--path={path}',
    ], cwd=tests_root)

    return r.returncode


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
