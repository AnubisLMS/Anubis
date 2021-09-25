from typing import Optional

from anubis.models import Config
from anubis.utils.cache import cache


@cache.memoize(timeout=10, source_check=True)
def get_config_str(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a config str entry for a given config key. Optionally specify a
    default value for if the key does not exist in the config table.

    :param key:
    :param default:
    :return:
    """

    # Query database for config row
    config_value: Config = Config.query.filter(Config.key == key).first()

    # Check that the config value exists
    if config_value is None:

        # Return default if entry was not found
        return default

    # Return the string value if it exists
    return config_value.value


@cache.memoize(timeout=10, source_check=True)
def get_config_int(key: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get a config int entry for a given config key. Optionally specify a
    default value for if the key does not exist in the config table.

    :param key:
    :param default:
    :return:
    """

    # Query database for config row
    config_value: Config = Config.query.filter(Config.key == key).first()

    # Check that the config value exists
    if config_value is None:
        # Return default if entry was not found
        return default

    # Attempt to convert and return the entry as an int
    try:
        # Try to convert the value to an int. This will raise a value
        # exception if there is any issue with the format with the
        # value.
        config_value_int = int(config_value.value.strip())

        # Pass back the converted integer value
        return config_value_int

    # ValueError will be raised if the underlying config value could
    # not be converted to an int.
    except ValueError:

        # If there was any issue, return default
        return default
