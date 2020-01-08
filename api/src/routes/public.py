from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError

from ..app import db
from ..models import Submissions, Results, Events

public = Blueprint('public', __name__, url_prefix='/public')


@public.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        pass
    return ''
