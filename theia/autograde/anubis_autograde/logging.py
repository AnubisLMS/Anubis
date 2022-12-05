import argparse
import logging

log = logging.getLogger('anubis-autograder')


def init_logging(args: argparse.Namespace):
    level = logging.DEBUG if args.verbose else logging.INFO
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s :: %(message)s')

    log.propagate = False
    log.setLevel(level)

    stream_log = logging.StreamHandler()
    stream_log.setLevel(level)
    stream_log.setFormatter(formatter)
    log.addHandler(stream_log)

    if args.log_file:
        debug_log = logging.FileHandler(args.log_file)
        debug_log.setLevel(level)
        debug_log.setFormatter(formatter)
        log.addHandler(debug_log)
