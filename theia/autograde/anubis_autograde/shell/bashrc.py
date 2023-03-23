import argparse
import os

from anubis_autograde.exercise.get import get_exercises
from anubis_autograde.logging import log
from anubis_autograde.shell.templates import bashrc_template


def init_bashrc(args: argparse.Namespace):
    exercises = get_exercises()

    home = os.environ['HOME']
    bashrc_dir = home if args.prod else os.getcwd()
    bashrc_path = os.path.join(bashrc_dir, '.bashrc')

    log.info(f'Generating shell rc bashrc_path={bashrc_path} exercises={exercises}')

    bashrc = bashrc_template.render(exercises=exercises)
    log.debug(bashrc)
    with open(bashrc_path, 'w') as bashrc_file:
        bashrc_file.write(bashrc)
