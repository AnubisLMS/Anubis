from flask import Flask
from anubis.config import config
from anubis.utils.data import is_debug
from anubis.utils.logging import logger


def add_sentry(_: Flask):
    if not is_debug() and config.SENTRY_DSN != '':
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        logger.info('ADDING SENTRY')
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[FlaskIntegration()],

            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0

            # By default the SDK will try to use the SENTRY_RELEASE
            # environment variable, or infer a git commit
            # SHA as release, however you may want to set
            # something more human-readable.
            # release="myapp@1.0.0",
        )

