import argparse
import os

from anubis_autograde.logging import log


def run_debug_shell(_: argparse.Namespace):
    if not os.path.exists('.bashrc'):
        log.error(f'.bashrc does not exist. Please run in directory with autograde server running.')
        exit(1)
    os.system('bash --rcfile .bashrc')
