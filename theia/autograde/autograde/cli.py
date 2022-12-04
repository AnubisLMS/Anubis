import argparse

from autograde.logging import init_logging
from autograde.server import run_server
from autograde.shell import run_debug_shell


def noargs(_):
    parser = make_parser()
    parser.print_help()
    exit(1)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Anubis live autograder')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-l', '--log_file', dest='log_file', default=None, help='File to log to (as well as console)')
    parser.set_defaults(func=noargs)

    subparsers = parser.add_subparsers(title='sub-commands',
                                       help='sub-command help',
                                       dest='subparser')

    # server
    parser_server = subparsers.add_parser('server', help='run autograde server')
    parser_server.add_argument('--bind', default='0.0.0.0:5003', help='Address to bind gunicorn server to')
    parser_server.add_argument('--token', default=None, help='')
    parser_server.add_argument('--netid', default=None, help='')
    parser_server.add_argument('--test', action='store_true')
    parser_server.add_argument('exercise_module')
    parser_server.set_defaults(func=run_server)

    parser_shell = subparsers.add_parser('shell',
                                         help='run autograde shell (for debugging). run from directory server is running in')
    parser_shell.set_defaults(func=run_debug_shell)

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    init_logging(args)
    args.func(args)
