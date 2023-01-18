import argparse
import traceback

import gunicorn.app.base
from flask import Flask

from anubis_autograde.exercise.get import get_exercises, get_end_message, get_start_message
from anubis_autograde.exercise.init import init_exercises
from anubis_autograde.exercise.pipeline import initialize_submission_status
from anubis_autograde.logging import init_server_logging, log
from anubis_autograde.server.views import views
from anubis_autograde.shell.bashrc import init_bashrc
from anubis_autograde.models import Exercise


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


def create_app(args: argparse.Namespace, skip_exercises: bool = False) -> Flask:
    app = Flask(__name__)

    if not skip_exercises:
        log.info(f'Loading exercises')
        init_exercises(args)

    app.config['SUBMISSION_ID'] = args.submission_id
    app.config['TOKEN'] = args.token
    app.config['DEBUG'] = args.debug
    app.config['PROD'] = args.prod
    app.config['RESUME'] = args.resume

    log.info(f'submission_id = {args.submission_id}')
    log.info(f'token = {args.token}')
    log.info(f'debug = {args.debug}')
    log.info(f'prod = {args.prod}')
    log.info(f'resume = {args.resume}')

    if args.prod:
        with app.app_context():
            try:
                initialize_submission_status()
            except Exception as e:
                log.error(traceback.format_exc()  + f'\nFailed to call {initialize_submission_status} Exception={e}')

    app.register_blueprint(views)

    init_server_logging(app)
    init_bashrc(args)

    return app


def run_server(args: argparse.Namespace):
    app = create_app(args)

    if args.spot_check:
        assert isinstance(get_start_message(), str)
        assert isinstance(get_end_message(), str)
        assert all(isinstance(exercise, Exercise) for exercise in get_exercises())
        log.info(f'Spot check passed')
        exit(0)

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
