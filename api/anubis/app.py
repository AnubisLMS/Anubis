from flask import Flask


def init_services(app: Flask):
    """
    Initialize app with redis cache, mariadb database, and ELK services

    :param app: Flask app
    :return:
    """
    from anubis.models import db
    from anubis.utils.cache import cache
    from anubis.utils.exceptions import add_app_exception_handlers
    from anubis.utils.migrate import migrate
    from anubis.utils.healthcheck import add_healthcheck
    from anubis.utils.sentry import add_sentry

    # Init services
    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    add_app_exception_handlers(app)
    add_healthcheck(app)
    add_sentry(app)

    db.app = app
    cache.app = app


def create_app() -> Flask:
    """
    Create the main Anubis API Flask app instance

    This app will have the basic services (db and cache),
    with the public and private blueprints.

    :return: Flask app
    """
    from anubis.env import env

    # Import views
    from anubis.views.admin import register_admin_views
    from anubis.views.public import register_public_views
    from anubis.views.super import register_super_views

    # Create app
    app = Flask(__name__)
    app.config.from_object(env)

    # Initialize app with all the extra services
    init_services(app)

    register_public_views(app)
    register_admin_views(app)
    register_super_views(app)

    @app.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    return app


def create_pipeline_app() -> Flask:
    """
    Create the Submission Pipeline API Flask app instance

    This app will have the basic services (db and cache),
    with the pipeline blueprint.

    :return: Flask app
    """
    from anubis.env import env
    from anubis.views.pipeline import register_pipeline_views

    # Create app
    app = Flask(__name__)
    app.config.from_object(env)

    # Initialize app with all the extra services
    init_services(app)

    # register views
    register_pipeline_views(app)

    return app
