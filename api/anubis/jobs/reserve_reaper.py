from anubis.constants import REAPER_TXT
from anubis.utils.data import with_context
from anubis.lms.reserve import reserve_sync

@with_context
def reap():
    reserve_sync()


if __name__ == "__main__":
    print(REAPER_TXT)

    reap()
