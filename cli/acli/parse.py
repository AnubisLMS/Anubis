import argparse
import sys
from .manpages import *

def parse_args(argv):
    if len(argv) == 0:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser('Anubis CLI')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debug mode (connect on localhost)')
    parser.add_argument('-u', '--user', dest='auth_username', required=False, help='specify user email')
    parser.add_argument('-p', '--password', dest='auth_password', required=False, help='specify user password')

    subparsers = parser.add_subparsers(dest='command')

    logout_parser = add_logout_parser(subparsers)
    ls_parser = add_ls_parser(subparsers)
    student_parser = add_student_parser(subparsers)
    restart_parser = add_restart_parser(subparsers)
    stats_parser = add_stats_parser(subparsers)
    dangling_parser = add_dangling_parser(subparsers)

    return parser.parse_args(argv), {
        'main': parser,
        'ls': ls_parser,
        'logout': logout_parser,
        'student': student_parser,
        'restart': restart_parser,
        'dangling': dangling_parser,
        'stats': stats_parser
    }



def add_restart_parser(subparsers):
    # Restart
    restart_parser = subparsers.add_parser(
        'restart',
        help='restart/re-enqueue submission jobs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    restart_parser.add_argument('netid', help='netid of student to restart')
    restart_parser.add_argument('commit', nargs='?', default=None, help='git commit hash to re-enqueue')

    return restart_parser



def add_stats_parser(subparsers):
    # Stats
    stats_parser = subparsers.add_parser(
        'stats',
        help='view submission stats for an assignment ',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    stats_parser.add_argument('assignment', help='name of assignment')
    stats_parser.add_argument('netid', nargs='?', default=None, help='netid to view')

    return stats_parser



def add_student_parser(subparsers):
    # Student
    student_parser = subparsers.add_parser(
        'student',
        help='students/re-enqueue submission jobs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=student_man,
    )

    student_parser.add_argument('filename', nargs='?', default=None, help='json file of student data')

    return student_parser


def add_dangling_parser(subparsers):
    # Dangling
    dangling_parser = subparsers.add_parser('dangling', help='attempt to repair dangling submissions')
    dangling_subparser = dangling_parser.add_subparsers(dest='subcommand')
    return dangling_parser


def add_logout_parser(subparsers):
    # Logout
    logout_parser = subparsers.add_parser('logout', help='delete credentials')
    logout_subparser = logout_parser.add_subparsers(dest='subcommand')
    return logout_parser


def add_ls_parser(subparsers):
    # Ls
    ls_parser = subparsers.add_parser('ls', help='list currently running / pending submissions')
    ls_subparser = ls_parser.add_subparsers(dest='subcommand')
    return ls_parser

