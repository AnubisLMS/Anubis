import functools
import argparse
import requests
import urllib3
import getpass
import json
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        action='store_true',
        dest='debug',
        help='debug mode (connect to localhost)'
    )
    parser.add_argument(
        '-u', '--user',
        dest='username',
        help='username'
    )
    parser.add_argument(
        '-p', '--password',
        dest='password',
        help='password'
    )
    parser.add_argument(
        'command',
        choices=[
            'ls',
            'restart',
            'stats',
            'student',
            'logout',
            'dangling'
        ],
        help='command to run'
    )
    parser.add_argument(
        'argv',
        nargs='*',
        help='command arguments'
    )
    return parser.parse_args()


def display(res):
    """
    This is used by the command wrapper to pretty print the json response
    for a request.

    :res: requests response object
    """
    if res.status_code == 200:
        print(json.dumps(res.json(), indent=2))
    else:
        print(res.status_code, res.content.decode())


def command(function):
    """
    This descriptor should be used on any function that handles a command.
    When the funtion returns the requests response object, this wrapper passes
    it to the display function. That will pretty print the response.

    :function: function to wrap
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        res = function(*args, **kwargs)
        display(res)
        return res
    return wrapper


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
    home=os.environ.get('HOME', '')

    if os.path.exists(os.path.join(home, '.anubis', 'creds.json')):
        creds = json.load(open(os.path.join(home, '.anubis', 'creds.json')))
        args.username = creds['username']
        args.password = creds['password']

    username = input('enter username: ') if not args.username else args.username
    password = getpass.getpass('enter password: ') if not args.password else args.password

    os.makedirs(os.path.join(home, '.anubis'), exist_ok=True)
    json.dump({'username': username, 'password': password}, open(os.path.join(home, '.anubis', 'creds.json'), 'w'))

    s.auth = (username, password,)
    s.url = 'https://os3224.nyu.cool' if not args.debug else 'https://localhost'
    return s


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
    if len(args.argv) == 1:
        body={
            'netid': args.argv[0]
        }
    elif len(args.argv) == 3:
        body={
            'netid': args.argv[0],
            'commit': args.argv[2],
        }
    else:
        print('invalid arguments')
        print('acli restart <netid> <commit>')
        exit(1)
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
    if len(args.argv) == 1:
        return s.post(s.url + '/private/student', json=json.load(open(args.argv[0])))
    elif len(args.argv) == 0:
        return s.get(s.url + '/private/student')
    else:
        print('acli student')
        print('acli student <filename.json>')
        exit(1)



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
    return s.get(s.url + os.path.join('/private/stats/', *args.argv))


def main():
    args=parse_args()

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
