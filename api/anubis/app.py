import logging

import logstash
from flask import Flask
from anubis.utils.logger import logger

def init_services(app):
    """
    Initialize app with redis cache, mariadb database, and ELK services

    :param app: Flask app
    :return:
    """
    from anubis.models import db, Config
    from anubis.utils.cache import cache
    from anubis.utils.elastic import add_global_error_handler
    from anubis.config import config

    # Init services
    db.init_app(app)
    cache.init_app(app)

    # Initialize the DB
    with app.app_context():
        db.create_all()

        if Config.query.filter(Config.key == "MAX_JOBS").first() is None:
            c = Config(key='MAX_JOBS', value='10')
            db.session.add(c)
            db.session.commit()

    @app.route('/')
    def index():
        return 'Hello there...!'

    # Make app logger anubis logger
    app.logger = logger

    # Add ELK stuff
    if not config.DISABLE_ELK:
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
