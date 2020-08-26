import logging

import logstash
from flask import Flask
from anubis.utils.data import is_debug

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG if is_debug() else logging.INFO)
root_logger.addHandler(logging.StreamHandler())


def init_services(app):
    """
    Initialize app with redis cache, mariadb database, and ELK services

    :param app: Flask app
    :return:
    """
    from anubis.models import db
    from anubis.utils.cache import cache
    from anubis.utils.elastic import add_global_error_handler
    from anubis.config import config

    # Init services
    db.init_app(app)
    cache.init_app(app)

    # Initialize the DB
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return 'Hello there...!'

    # Add ELK stuff
    if not config.DISABLE_ELK:
        # Add logstash handler
        app.logger.addHandler(logstash.LogstashHandler('logstash', 5000))
        root_logger.addHandler(logstash.LogstashHandler('logstash', 5000))

        # Add elastic global error handler
        add_global_error_handler(app)


def create_app():
    """
    Create the main Anubis API Flask app instance

    This app will have the basic services (db and cache),
    with the public and private blueprints.

    :return: Flask app
    """
    from anubis.config import config
    from anubis.routes.public import public
    from anubis.routes.private import private

    # Create app
    app = Flask(__name__)
    app.config.from_object(config)

    init_services(app)

    # register blueprints
    app.register_blueprint(public)
    app.register_blueprint(private)

    return app


def create_pipeline_app():
    """
    Create the Submission Pipeline API Flask app instance

    This app will have the basic services (db and cache),
    with the pipeline blueprint.

    :return: Flask app
    """
    from anubis.config import config
    from anubis.routes.pipeline import pipeline

    # Create app
    app = Flask(__name__)
    app.config.from_object(config)

    init_services(app)

    # register blueprints
    app.register_blueprint(pipeline)

    return app
