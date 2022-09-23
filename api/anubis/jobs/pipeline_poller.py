import os

if 'SENTRY_DSN' in os.environ:
    del os.environ['SENTRY_DSN']

from kubernetes import config

from anubis.utils.data import with_context
from anubis.k8s.pipeline import reap_pipeline_jobs


@with_context
def main():
    config.load_incluster_config()

    while True:
        reap_pipeline_jobs()


if __name__ == "__main__":
    main()