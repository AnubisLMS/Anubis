import functools
import argparse
import requests
import urllib3
import getpass
import json

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
            'restart'
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

    username = input('enter username: ') if not args.username else args.username
    password = getpass.getpass('enter password: ') if not args.password else args.password
    s.auth = (username, password,)
    s.url = 'https://os3224.nyu.cool' if not args.debug else 'https://localhost'
    return s


@command
def ls(args):
    """
    Lists the currently processing submissions.

    :args: parsed ArgumentParser object
    """
    s=get_session(args)
    return s.get(s.url + '/private/ls')


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


def main():
    args=parse_args()

    if args.command == 'ls':
        ls(args)
    elif args.command == 'restart':
        restart(args)
    else:
        print('')
        exit(1)


if __name__ == '__main__':
    main()
