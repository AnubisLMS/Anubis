import os

from anubis_autograde.logging import init_logging
from anubis_autograde.parser import make_parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    init_logging(args)
    args.func(args)
