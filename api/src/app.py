from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

from .config import Config

app = Flask(__name__)
app.config.from_object(Config())
cache = Cache(app,config={'CACHE_TYPE': 'redis'})

db = SQLAlchemy(app)


@app.route('/')
def index():
    return 'Hello'

from .routes import public, private
app.register_blueprint(public)
app.register_blueprint(private)


from .utils import add_global_error_handler
add_global_error_handler(app)
