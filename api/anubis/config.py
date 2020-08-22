import logging
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://anubis:anubis@{}/anubis'.format(
        os.environ.get('DB_HOST', 'db')
    )
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMINS = os.environ.get('ADMINS', 'jmc1283@nyu.edu')

    CACHE_REDIS_HOST = 'redis'

    def __init__(self):
        logging.info('Starting Anubis API with SECRET_KEY: {}'.format(self.SECRET_KEY))
        if os.environ.get('DEBUG', None):
            self.DEBUG = True
