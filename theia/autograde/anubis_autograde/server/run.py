import argparse
import logging

import gunicorn.app.base

from anubis_autograde.exercise.init import init_exercises
from anubis_autograde.server.app import app
from anubis_autograde.shell.bashrc import init_bashrc


class _StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, _app, options=None):
        self.options = options or {}
        self.application = _app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def init_server_logging():
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def run_server(args: argparse.Namespace):
    init_server_logging()
    init_exercises(args)
    init_bashrc(args)
    if args.debug:
        host, port = args.bind.split(':')
        exercise_module = args.exercise_module \
            if not args.exercise_module.endswith('.py') \
            else args.exercise_module + '.py'
        app.run(host, port, debug=True, extra_files=[exercise_module])

    else:
        _StandaloneApplication(
            app, options={
                'bind':                     args.bind,
                'workers':                  1,
                'capture-output':           True,
                'enable-stdio-inheritance': True,
            }
            ).run()
