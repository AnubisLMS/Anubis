import logging
import os

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

import logstash
from .config import Config

app = Flask(__name__)
app.config.from_object(Config())
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

db = SQLAlchemy(app)

if os.environ.get('DISABLE_ELK', default='0') != '1':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(logstash.LogstashHandler('logstash', 5000))
    root_logger.addHandler(logging.StreamHandler())


@app.route('/')
def index():
    return 'Hello from the other side'


from .routes import public, private

app.register_blueprint(public)
app.register_blueprint(private)

from .utils.elastic import add_global_error_handler

add_global_error_handler(app)
