import argparse
import os

from autograde.logging import log


def run_debug_shell(_: argparse.Namespace):
    if os.path.exists('.bashrc'):
        log.error(f'')
    os.system('bash --rcfile .bashrc')
