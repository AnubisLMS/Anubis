from flask import Flask
from anubis.utils.logger import logger


def init_services(app):
    """
    Initialize app with redis cache, mariadb database, and ELK services

    :param app: Flask app
    :return:
    """
    from anubis.models import db
    from anubis.utils.cache import cache
    from anubis.utils.migrate import migrate
    from anubis.utils.elastic import add_global_error_handler
    from anubis.config import config

    # Init services
    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def index():
        return "Hello there..."

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

    # Import views
    from anubis.views.public import register_public_views
    from anubis.views.admin import register_admin_views

    # Create app
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize app with all the extra services
    init_services(app)

    # register views
    register_public_views(app)
    register_admin_views(app)

    return app


def create_pipeline_app():
    """
    Create the Submission Pipeline API Flask app instance

    This app will have the basic services (db and cache),
    with the pipeline blueprint.

    :return: Flask app
    """
    from anubis.config import config
    from anubis.views.pipeline import register_pipeline_views

    # Create app
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize app with all the extra services
    init_services(app)

    # register blueprints
    register_pipeline_views(app)

    return app
