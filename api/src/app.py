from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import Config

app = Flask(__name__)
app.config.from_object(Config())

db = SQLAlchemy(app)


@app.route('/')
def index():
    return 'Hello'

from .routes import public, private
app.register_blueprint(public)
app.register_blueprint(private)


db.create_all()
