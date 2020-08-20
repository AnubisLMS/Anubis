import logging
from typing import Union

import jwt
from flask import request

from api.anubis import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(128), unique=True, index=True)
    github_username = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128))
    admin = db.Column(db.Boolean, nullable=False, default=False)

    @staticmethod
    def load_user(netid: Union[str, None]):
        """
        Load a user by username

        :param netid: netid of wanted user
        :return: User object or None
        """
        if netid is None:
            return None
        u1 = User.query.filter_by(netid=netid).first()

        logging.debug(f'loading user {u1.data}')

        return u1

    @staticmethod
    def current_user():
        """
        Load current user based on the token

        :return: User or None
        """
        token = request.headers.get('token', default=None)
        if token is None:
            return None

        try:
            # TODO update secret key
            decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
        except Exception as e:
            return None

        if 'netid' not in decoded:
            return None

        return User.load_user(decoded['netid'])

    @property
    def token(self):
        return jwt.encode({
            'netid': self.netid,
            # 'exp': datetime.utcnow() + timedelta(weeks=4),
            # TODO update secret key
        }, 'secret', algorithm='HS256').decode()

    @property
    def data(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'github_username': self.github_username,
            'name': self.name,
            'admin': self.admin,
        }