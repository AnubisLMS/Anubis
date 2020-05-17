import json
import os

from .auth import get_session
from .parse import parse_args
from .utils import command

parsers = None


def logout(_):
    """
    Yeet creds
    """
    home = os.environ.get('HOME', '')
    if os.path.exists(os.path.join(home, '.anubis', 'creds.json')):
        os.remove(os.path.join(home, '.anubis', 'creds.json'))
    print('logged out')


@command
def ls(args):
    """
    Lists the currently processing submissions.

    :args: parsed ArgumentParser object
    """
    s = get_session(args)
    return s.get(s.url + '/private/ls')


@command
def dangling(args):
    """
    Lists the currently dangling submissions.

    :args: parsed ArgumentParser object
    """
    s = get_session(args)
    return s.get(s.url + '/private/dangling')


@command
def student(args):
    """
    upload, or update studnet values
    from a json

    acli student <filename.json>

    :args: parserd ArugmentParser object
    """
    s = get_session(args)
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
    s = get_session(args)
    netids = None
    s.headers.clear()
    if args.file is not None:
        if args.file.endswith('.json'):
            netids = json.load(open(args.file, 'r'))
        else:
            netids = [
                l.strip()
                for l in open(args.file, 'r').readlines()
            ]
    if netids is not None:
        return s.get(
            s.url + os.path.join('/private/stats/', args.assignment),
            params={
                'netids': json.dumps(netids)
            }
        )
    if args.netid is None:
        return s.get(s.url + os.path.join('/private/stats/', args.assignment))
    return s.get(s.url + os.path.join('/private/stats/', args.assignment, args.netid))


@command
def assignment(args):
    """
    Add or edit an assignment.
    Datetimes should be in format: '2020-03-02 23:40:58'

    anubis assignment add 'assignment name' 'due date' 'grace date'
    anubis assignment modify 'assignment name' 'new due date' 'new grace date'

    :args: parsed ArgumentParser object
    """

    if not args.subcommand:
        parsers['assignment'].print_help()
        exit(0)

    s = get_session(args)
    return s.post(s.url + '/private/assignment', json={
        'data': {
            'name': args.name if 'name' in args else None,
            'due_date': args.due_date if 'due_date' in args else None,
            'grace_date': args.grace_date if 'grace_date' in args else None,
        },
        'action': args.subcommand,
    })


@command
def finalquestions(args):
    """
    [
      {
        content
        level
        solution?
      }
    ]
    :param args:
    :return:
    """
    s = get_session(args)
    if args.filename is None:
        return s.get(s.url + '/private/finalquestions')
    return s.post(s.url + '/private/finalquestions', json=json.load(open(args.filename)))


def main(*argv):
    global parsers
    args, parsers = parse_args(argv)

    if not args.command:
        parsers['main'].print_help()
        exit()

    {
        'ls': ls,
        'dangling': dangling,
        'stats': stats,
        'student': student,
        'logout': logout,
        'assignment': assignment,
        'fq': finalquestions
    }[args.command](args)


if __name__ == '__main__':
    main()
