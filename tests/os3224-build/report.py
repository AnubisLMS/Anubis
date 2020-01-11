#!/usr/bin/python3
from argparse import ArgumentParser
from .utils import report_all

def parse_args():
    parser = ArgumentParser('Use this script to report results to the api')
    parser.add_argument('netid', nargs=1, required=True, help='student netid')
    parser.add_argument('assignment', nargs=1, required=True, help='assignment being graded')
    return parser.parse_args()

def main():
    args = parse_args()
    report_all(
        args.netid,
        args.assignment
    )


if __name__ == "__main__":
    main()
