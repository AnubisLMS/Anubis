from flask import Flask


def init_services(app):
    """
    Initialize app with redis cache, mariadb database, and ELK services

    :param app: Flask app
    :return:
    """
    from anubis.config import config
    from anubis.models import db, Config
    from anubis.utils.services.cache import cache, cache_health
    from anubis.utils.services.migrate import migrate
    from anubis.utils.exceptions import add_app_exception_handlers

    # Init services
    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    add_app_exception_handlers(app)

    @app.route("/")
    def index():
        Config.query.all()
        cache_health()
        return "Healthy"


def create_app():
    """
    Create the main Anubis API Flask app instance

    This app will have the basic services (db and cache),
    with the public and private blueprints.

    :return: Flask app
    """
    from anubis.config import Config

    # Import views
    from anubis.views.public import register_public_views
    from anubis.views.admin import register_admin_views

    # Create app
    app = Flask(__name__)
    app.config.from_object(Config())

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

    # register views
    register_pipeline_views(app)

    return app
