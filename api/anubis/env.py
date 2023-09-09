import os


class EnvConfig(object):
    def __init__(self):
        # General flask config
        self.MINDEBUG = os.environ.get("MINDEBUG", default="0") == "1"
        self.DEBUG = os.environ.get("DEBUG", default="0") == "1" or self.MINDEBUG
        self.JOB = os.environ.get("JOB", default="0") == "1"
        self.SECRET_KEY = os.environ.get("SECRET_KEY", default="DEBUG")
        self.DB_HOST = os.environ.get("DB_HOST", "db")
        self.REDIS_HOST = os.environ.get("REDIS_HOST", "redis-master")
        self.REDIS_PASS = os.environ.get("REDIS_PASS", default="anubis")
        self.DOMAIN = os.environ.get("DOMAIN", default="localhost")
        self.SENTRY_DSN = os.environ.get("SENTRY_DSN", default=None)
        self.IDE_NODE_SELECTOR = os.environ.get("IDE_NODE_SELECTOR", default=None)
        self.DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", default=None)

        if not self.MINDEBUG:
            # sqlalchemy
            self.SQLALCHEMY_POOL_PRE_PING = True
            self.SQLALCHEMY_POOL_SIZE = 100
            self.SQLALCHEMY_POOL_RECYCLE = 280
            self.SQLALCHEMY_TRACK_MODIFICATIONS = False
            self.SQLALCHEMY_DATABASE_URI = os.environ.get(
                "DATABASE_URI",
                default="mysql+pymysql://anubis:anubis@{}/anubis".format(self.DB_HOST),
            )
            # self.SQLALCHEMY_ECHO = True

            # cache
            self.CACHE_TYPE = "RedisCache"
            self.CACHE_REDIS_HOST = self.REDIS_HOST
            self.CACHE_REDIS_PASSWORD = self.REDIS_PASS

        # MINDEBUG
        else:
            os.makedirs(".data/", exist_ok=True)

            # sqlalchemy
            self.SQLALCHEMY_DATABASE_URI = "sqlite:///../.data/anubis.db"
            self.SQLALCHEMY_TRACK_MODIFICATIONS = False

            # cache
            self.CACHE_TYPE = "NullCache"

        # OAuth
        self.OAUTH_NYU_CONSUMER_KEY = os.environ.get("OAUTH_NYU_CONSUMER_KEY", default="DEBUG")
        self.OAUTH_NYU_CONSUMER_SECRET = os.environ.get("OAUTH_NYU_CONSUMER_SECRET", default="DEBUG")

        # Github OAuth
        self.OAUTH_GITHUB_CONSUMER_KEY = os.environ.get("OAUTH_GITHUB_CONSUMER_KEY", default="DEBUG")
        self.OAUTH_GITHUB_CONSUMER_SECRET = os.environ.get("OAUTH_GITHUB_CONSUMER_SECRET", default="DEBUG")

        # Github Tag
        self.GIT_TAG = os.environ.get("GIT_TAG", default="latest")

        # Logger
        self.LOGGER_NAME = os.environ.get("LOGGER_NAME", default="anubis-api")

        print("Starting with DATABASE_URI: {}".format(self.SQLALCHEMY_DATABASE_URI))
        print("Starting with CACHE_TYPE: {}".format(self.CACHE_TYPE))
        print("Starting with SECRET_KEY: {}".format(self.SECRET_KEY))
        print("Starting with MINDEBUG: {}".format(self.MINDEBUG))
        print("Starting with DEBUG: {}".format(self.DEBUG))


env = EnvConfig()
