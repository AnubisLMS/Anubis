import logging
import os
import hashlib


class Config:
    SECRET_KEY = None

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OAuth
    OAUTH_CONSUMER_KEY = ""
    OAUTH_CONSUMER_SECRET = ""

    # Cache config
    CACHE_REDIS_HOST = "redis-master"
    CACHE_REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", default="anubis")

    # Logger config
    LOGGER_NAME = os.environ.get("LOGGER_NAME", default="anubis-api")

    # Theia config
    THEIA_DOMAIN = ""

    def __init__(self):
        self.DEBUG = os.environ.get("DEBUG", default="0") == "1"

        self.SECRET_KEY = os.environ.get("SECRET_KEY", default="DEBUG")

        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URI",
            default="mysql+pymysql://anubis:anubis@{}/anubis".format(
                os.environ.get("DB_HOST", "db")
            ),
        )
        self.DISABLE_ELK = os.environ.get("DISABLE_ELK", default="0") == "1"

        # OAuth
        self.OAUTH_CONSUMER_KEY = os.environ.get("OAUTH_CONSUMER_KEY", default="DEBUG")
        self.OAUTH_CONSUMER_SECRET = os.environ.get(
            "OAUTH_CONSUMER_SECRET", default="DEBUG"
        )

        # Redis
        self.CACHE_REDIS_HOST = os.environ.get(
            "CACHE_REDIS_HOST", default="redis-master"
        )

        self.CACHE_REDIS_PASSWORD = os.environ.get(
            "REDIS_PASS", default="anubis"
        )

        # Logger
        self.LOGGER_NAME = os.environ.get("LOGGER_NAME", default="anubis-api")

        # Theia
        self.THEIA_DOMAIN = os.environ.get(
            "THEIA_DOMAIN", default="ide.anubis.osiris.services"
        )

        logging.info(
            "Starting with DATABASE_URI: {}".format(self.SQLALCHEMY_DATABASE_URI)
        )
        logging.info("Starting with SECRET_KEY: {}".format(self.SECRET_KEY))
        logging.info("Starting with DEBUG: {}".format(self.DEBUG))


config = Config()
