import logging
import os

import logstash
from flask import Flask


def create_app():
    from anubis.config import Config
    from anubis.routes.public import public
    from anubis.routes.private import private
    from anubis.utils.elastic import add_global_error_handler
    from anubis.models import db
    from anubis.utils.cache import cache

    app = Flask(__name__)
    app.config.from_object(Config())
    db.init_app(app)
    cache.init_app(app)

    app.register_blueprint(public)
    app.register_blueprint(private)
    add_global_error_handler(app)


    @app.route('/')
    def index():
        return 'Hello from the other side'

    return app


if os.environ.get('DISABLE_ELK', default='0') != '1':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(logstash.LogstashHandler('logstash', 5000))
    root_logger.addHandler(logging.StreamHandler())
