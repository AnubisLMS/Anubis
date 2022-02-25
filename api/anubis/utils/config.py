import json
from typing import Optional, Dict

from anubis.models import db, Config
from anubis.utils.cache import cache


def set_config_value(key: str, value: str) -> Config:
    # Find existing config
    config: Config = Config.query.filter(Config.key == key).first()

    # If config does not exist, add it
    if config is None:
        config: Config = Config(key=key)
        db.session.add(config)

    # Set value
    config.value = value

    # Commit change
    db.session.commit()


@cache.memoize(timeout=10, source_check=True)
def get_config_dict(key: str, default: Optional[Dict] = None) -> Optional[Dict]:
    """
    Get a config str entry for a given config key. Optionally specify a
    default value for if the key does not exist in the config table.

    :param key:
    :param default:
    :return:
    """

    # Query database for config row
    config_value_raw: Config = Config.query.filter(Config.key == key).first()

    # Check that the config value exists
    if config_value_raw is None:
        # Return default if entry was not found
        return default

    # Return the parsed json value if we are able
    try:
        return json.loads(config_value_raw.value)
    except json.JSONDecodeError:
        return default


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
