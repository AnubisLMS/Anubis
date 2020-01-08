from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..models import Submissions, Results, Events

private = Blueprint('private', __name__, url_prefix='/private')

@private.route('/')
def index():
    return 'super secret'

