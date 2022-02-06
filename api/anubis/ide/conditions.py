from anubis.utils.config import get_config_int
from anubis.utils.data import req_assert


def assert_theia_sessions_enabled():
    # Get the config value for if ide starts are allowed.
    theia_starts_enabled = get_config_int("THEIA_STARTS_ENABLED", default=1) == 1

    # Assert that new ide starts are allowed. If they are not, then
    # we return a status message to the user saying they are not able
    # to start a new ide.
    req_assert(
        theia_starts_enabled,
        message="Starting new IDEs is currently disabled by an Anubis administrator. " "Please try again later.",
    )