from flask import Flask
from anubis.env import env
from anubis.utils.data import is_debug, is_job
from anubis.utils.logging import logger


def traces_sampler(sampling_context):
    # Examine provided context data (including parent decision, if any)
    # along with anything in the global namespace to compute the sample rate
    # or sampling decision for this transaction

    if 'REQUEST_URI' in sampling_context and sampling_context['REQUEST_URI'] == '/':
        return 0
    else:
        # Default sample rate
        return 0.25


def add_sentry(app: Flask):
    if not is_debug() and env.SENTRY_DSN != '' and env.SENTRY_DSN is not None:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        logger.info('ADDING SENTRY')

        sentry_sdk.init(
            dsn=env.SENTRY_DSN,
            integrations=[FlaskIntegration()] if not is_job() else [],

            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,

            # By default the SDK will try to use the SENTRY_RELEASE
            # environment variable, or infer a git commit
            # SHA as release, however you may want to set
            # something more human-readable.
            # release="myapp@1.0.0",
            traces_sampler=traces_sampler,
        )

