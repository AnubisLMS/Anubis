from anubis.constants import REAPER_TXT
from anubis.rpc.enqueue import reap_stale_theia_sessions
from anubis.utils.data import with_context


@with_context
def reap():
    # Enqueue a job to reap stale ide k8s resources
    reap_stale_theia_sessions()


if __name__ == "__main__":
    print(REAPER_TXT)

    reap()
