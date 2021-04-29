import logging
import os
from datetime import timedelta


class Config:

    def __init__(self):
        # General flask config
        self.DEBUG = os.environ.get("DEBUG", default="0") == "1"
        self.SECRET_KEY = os.environ.get("SECRET_KEY", default="DEBUG")

        # sqlalchemy
        self.SQLALCHEMY_DATABASE_URI = None
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

        # Elasticsearch
        self.DISABLE_ELK = os.environ.get("DISABLE_ELK", default="0") == "1"

        # OAuth
        self.OAUTH_CONSUMER_KEY = os.environ.get("OAUTH_CONSUMER_KEY", default="DEBUG")
        self.OAUTH_CONSUMER_SECRET = os.environ.get("OAUTH_CONSUMER_SECRET", default="DEBUG")

        # Redis
        self.CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_HOST", default="redis-master")
        self.CACHE_REDIS_PASSWORD = os.environ.get("REDIS_PASS", default="anubis")

        # Logger
        self.LOGGER_NAME = os.environ.get("LOGGER_NAME", default="anubis-api")

        # Theia
        self.THEIA_DOMAIN = os.environ.get("THEIA_DOMAIN", default="ide.anubis.osiris.services")
        self.THEIA_TIMEOUT = timedelta(hours=6)

        # autograding specific config
        self.STATS_REAP_DURATION = timedelta(days=60)

        logging.info("Starting with DATABASE_URI: {}".format(self.SQLALCHEMY_DATABASE_URI))
        logging.info("Starting with SECRET_KEY: {}".format(self.SECRET_KEY))
        logging.info("Starting with DEBUG: {}".format(self.DEBUG))


config = Config()
