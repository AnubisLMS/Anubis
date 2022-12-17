import os

from anubis_autograde.logging import init_logging
from anubis_autograde.parser import make_parser


def main():
    os.environ['FORCE_COLOR'] = 'true'
    parser = make_parser()
    args = parser.parse_args()
    init_logging(args)
    args.func(args)
