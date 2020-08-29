"""Console script for anubis."""
import sys

import click
import requests
import yaml
import sys
import os
import json

sys.path.append(os.getcwd())

API_URL = 'https://anubis.osiris.services/api'
conf_dir = os.path.join(os.environ.get("HOME"), ".anubis")
conf_file = os.path.join(os.environ.get("HOME"), ".anubis/config.json")



def load_conf():
    init_conf()
    return json.load(open(conf_file))


def set_conf(conf):
    init_conf()
    json.dumps(conf, open(conf_file, 'w'))


def init_conf():
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir, exists_ok=True)

    if not os.path.isfile(conf_file):
        set_conf({"auth":{"username": None, "password": None}})


def load_auth():
    conf = load_conf()
    return conf['auth']['username'], conf['auth']['password']


def set_auth(username, password):
    init_conf()
    conf['auth']['username'] = username
    conf['auth']['password'] = password
    set_conf(conf)


def post_json(path, data):
    auth = load_auth()
    if load_auth == (None, None):
        raise
    res = requests.post(
        API_URL + path,
        headers={'Content-Type': 'application/json'},
        json=data,
        auth=auth,
    )
    return res


@click.group()
@click.option('--debug/-d', default=False)
@click.option('--username/-u', default=None)
@click.option('--password/-p', default=None)
def main(debug, username, password):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    if debug:
        global API_URL
        API_URL = 'http://localhost:5000'

    if username is not None or password is not None:
        c_username, c_password = load_auth()
        set_auth(username or c_username, password or c_password)


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
    r = requests.post(
        'http://localhost:5000/private/assignment/sync',
        headers={'Content-Type': 'application/json'},
        json=assignment_meta
    )
    click.echo(json.dumps(r.json(), indent=2))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
