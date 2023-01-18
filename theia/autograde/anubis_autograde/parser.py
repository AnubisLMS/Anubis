import argparse

from anubis_autograde.exercise.run import run_exercise_init
from anubis_autograde.server.run import run_server
from anubis_autograde.shell.run import run_debug_shell


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

    subparsers = parser.add_subparsers(
        title='sub-commands',
        help='sub-command help',
        dest='subparser'
        )

    # server
    parser_server = subparsers.add_parser('server', help='run autograde server')
    parser_server.add_argument('--bind', default='0.0.0.0:5003', help='Address to bind gunicorn server to')
    parser_server.add_argument('--token', default=None, help='autograder token used in production')
    parser_server.add_argument('--submission_id', default=None, help='Anubis submission id used in production')
    parser_server.add_argument('--netid', default=None, help='Netid of student used in production')
    parser_server.add_argument('--resume', default=None, help='Exercise to resume to')
    parser_server.add_argument('--prod', action='store_true', help='Enables production mode. This will overwrite the ')
    parser_server.add_argument('--spot_check', action='store_true', help='Spot check exercise.py. (Exit after initialization)')
    parser_server.add_argument('exercise_module')
    parser_server.set_defaults(func=run_server)

    # shell
    parser_shell = subparsers.add_parser(
        'shell',
        help='run autograde shell (for debugging). run from directory server is running in'
        )
    parser_shell.set_defaults(func=run_debug_shell)

    # exercise
    parser_exercise_init = subparsers.add_parser(
        'exercise-init',
        help='generate exercise.py from template'
        )
    parser_exercise_init.set_defaults(func=run_exercise_init)

    return parser
