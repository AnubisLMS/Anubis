import traceback

from flask import Flask


def add_healthcheck(app: Flask):
    from anubis.utils.http.decorators import json_response
    from anubis.models import Config
    from anubis.utils.cache import cache_health
    from anubis.utils.logging import logger
    from anubis.env import env

    @app.route("/")
    @json_response
    def index():
        """
        Healthcheck endpoint.

        This preforms a very basic check to make sure that the database
        and the cache are reachable on the current instance. If the status
        comes back as "Unhealthy", then there was some exception that was
        raised when attempting to connect to it. It may only be a temporary
        issue, or something specific to the instance it is running on.

        response = {
          "db": "Healthy",
          "cache": "Healthy"
        }

        :return:
        """

        # Construct basic status & status code
        status_code = 200
        status = {
            "service": env.LOGGER_NAME,
            "api": "Healthy",
            "db": "Healthy",
            "cache": "Healthy",
            "commit": env.GIT_TAG
        }

        # Attempt to connect to db
        try:
            Config.query.all()

        # If there is any issue, mark the db
        # connection as Unhealthy and log the error
        except Exception as e:
            status["db"] = "Unhealthy"
            status_code = 500
            logger.error(traceback.format_exc())

        # Attempt to connect to cache
        try:
            cache_health()

        # If there is any issue, mark the cache
        # connection as Unhealthy and log the error
        except Exception as e:
            status["cache"] = "Unhealthy"
            status_code = 500
            logger.error(traceback.format_exc())

        # Pass back status and status_code
        return status, status_code
