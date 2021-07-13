import logging
import os
from datetime import timedelta


class Config:

    def __init__(self):
        # General flask config
        self.MINDEBUG = os.environ.get("MINDEBUG", default="0") == "1"
        self.DEBUG = os.environ.get("DEBUG", default="0") == "1" or self.MINDEBUG
        self.JOB = os.environ.get('JOB', default='0') == '1'
        self.SECRET_KEY = os.environ.get("SECRET_KEY", default="DEBUG")

        if not self.MINDEBUG:
            # sqlalchemy
            self.SQLALCHEMY_POOL_PRE_PING = True
            self.SQLALCHEMY_POOL_SIZE = 100
            self.SQLALCHEMY_POOL_RECYCLE = 280
            self.SQLALCHEMY_TRACK_MODIFICATIONS = False
            self.SQLALCHEMY_DATABASE_URI = os.environ.get(
                "DATABASE_URI",
                default="mysql+pymysql://anubis:anubis@{}/anubis".format(
                    os.environ.get("DB_HOST", "db")
                ),
            )

            # cache
            self.CACHE_TYPE = 'RedisCache'
            self.CACHE_REDIS_HOST = os.environ.get("REDIS_HOST", default="redis-master")
            self.CACHE_REDIS_PASSWORD = os.environ.get("REDIS_PASS", default="anubis")

        # MINDEBUG
        else:
            os.makedirs('.data/', exist_ok=True)
            
            # sqlalchemy
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///../.data/anubis.db'
            self.SQLALCHEMY_TRACK_MODIFICATIONS = False

            # cache
            self.CACHE_TYPE = 'NullCache'

        # OAuth
        self.OAUTH_CONSUMER_KEY = os.environ.get("OAUTH_CONSUMER_KEY", default="DEBUG")
        self.OAUTH_CONSUMER_SECRET = os.environ.get("OAUTH_CONSUMER_SECRET", default="DEBUG")

        # Logger
        self.LOGGER_NAME = os.environ.get("LOGGER_NAME", default="anubis-api")

        # Theia
        self.THEIA_TIMEOUT = timedelta(hours=6)

        # autograding specific config
        self.STATS_REAP_DURATION = timedelta(days=60)

        print("Starting with DATABASE_URI: {}".format(self.SQLALCHEMY_DATABASE_URI))
        print("Starting with CACHE_TYPE: {}".format(self.CACHE_TYPE))
        print("Starting with SECRET_KEY: {}".format(self.SECRET_KEY))
        print("Starting with MINDEBUG: {}".format(self.MINDEBUG))
        print("Starting with DEBUG: {}".format(self.DEBUG))


config = Config()
