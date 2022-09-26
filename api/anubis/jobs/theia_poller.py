import os
import time

if 'SENTRY_DSN' in os.environ:
    del os.environ['SENTRY_DSN']

from kubernetes import config

from anubis.utils.data import with_context
from anubis.k8s.theia.update import update_all_theia_sessions


def main():
    config.load_incluster_config()

    while True:
        with_context(update_all_theia_sessions)()
        time.sleep(1)


if __name__ == "__main__":
    main()
