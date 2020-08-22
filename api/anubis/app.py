import logging

import logstash
from flask import Flask

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(logging.StreamHandler())


def create_app():
    from anubis.config import config
    from anubis.routes.public import public
    from anubis.routes.private import private
    from anubis.utils.elastic import add_global_error_handler
    from anubis.models import db
    from anubis.utils.cache import cache

    # Create app
    app = Flask(__name__)
    app.config.from_object(config)

    # Init services
    db.init_app(app)
    cache.init_app(app)

    # registry blueprints
    app.register_blueprint(public)
    app.register_blueprint(private)

    @app.route('/')
    def index():
        return 'Hello from the other side'

    # Initialize the DB
    with app.app_context():
        db.create_all()

    # Add ELK stuff
    if not config.DISABLE_ELK:
        # Add logstash handler
        app.logger.addHandler(logstash.LogstashHandler('logstash', 5000))
        root_logger.addHandler(logstash.LogstashHandler('logstash', 5000))

        # Add elastic global error handler
        add_global_error_handler(app)

    return app
