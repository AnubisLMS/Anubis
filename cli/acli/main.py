import requests
import urllib3
import getpass
import json
import os

from .parse import parse_args
from .auth import get_session
from .utils import command


def logout(_):
    """
    Yeet creds
    """
    home=os.environ.get('HOME', '')
    if os.path.exists(os.path.join(home, '.anubis', 'creds.json')):
        os.remove(os.path.join(home, '.anubis', 'creds.json'))
    print('logged out')


@command
def ls(args):
    """
    Lists the currently processing submissions.

    :args: parsed ArgumentParser object
    """
    s=get_session(args)
    return s.get(s.url + '/private/ls')

@command
def dangling(args):
    """
    Lists the currently dangling submissions.

    :args: parsed ArgumentParser object
    """
    s=get_session(args)
    return s.get(s.url + '/private/dangling')


@command
def restart(args):
    """
    Restart a submission job.

    Either specify a netid to restart the most recent submission,
    or specify a netid and a commit hash for a specific 

    acli restart <netid>
    acli restart <netid> <commit>

    :args: parsed ArgumentParser object
    """
    s=get_session(args)
    body={
        'netid': args.netid,
    }
    if args.commit is not None:
        body['commit'] = args.commit
    return s.post(s.url + '/private/restart', json=body)


@command
def student(args):
    """
    upload, or update studnet values
    from a json

    acli student <filename.json>

    :args: parserd ArugmentParser object
    """
    s=get_session(args)
    if args.filename is None:
        return s.get(s.url + '/private/student')
    return s.post(s.url + '/private/student', json=json.load(open(args.filename)))


@command
def stats(args):
    """
    Restart a submission job.

    Either specify a assignment or an assignment and a netid
    to get submission statistics.

    acli stats <assignment>
    acli stats <assignment> <netid>

    :args: parsed ArgumentParser object
    """
    s=get_session(args)
    s.headers.clear()
    if args.netid is None:
        return s.get(s.url + os.path.join('/private/stats/', args.assignment))
    return s.get(s.url + os.path.join('/private/stats/', args.assignment, args.netid))


def main(*argv):
    args, parsers = parse_args(argv)

    if not args.command:
        parsers['main'].print_help()
        exit()

    # if not args.subcommand:
    #     parsers[args.command].print_help()
    #     exit()

    {
        'ls': ls,
        'dangling': dangling,
        'restart': restart,
        'stats': stats,
        'student': student,
        'logout': logout,
    }[args.command](args)


if __name__ == '__main__':
    main()
