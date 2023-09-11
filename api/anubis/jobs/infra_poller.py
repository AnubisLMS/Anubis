import os
import time

if 'SENTRY_DSN' in os.environ:
    del os.environ['SENTRY_DSN']

from anubis.lms.theia import check_cluster_ides


def main():
    while True:
        check_cluster_ides()
        time.sleep(1)


if __name__ == "__main__":
    main()
