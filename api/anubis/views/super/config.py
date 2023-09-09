from flask import Blueprint

from anubis.models import Config, db
from anubis.utils.auth.http import require_superuser
from anubis.utils.http import success_response, req_assert
from anubis.utils.http.decorators import json_endpoint, json_response

config_ = Blueprint("config", __name__, url_prefix="/super/config")


@config_.route("/list")
@require_superuser()
@json_response
def config_list():
    """
    list all config items.

    :return:
    """

    # Pull all the config items
    items = Config.query.all()

    # Return the broken down objects
    return success_response({"config": [item.data for item in items]})


@config_.route("/save", methods=["POST"])
@require_superuser()
@json_endpoint(required_fields=[("config", dict)])
def config_add(config, **_):
    """

    config = [
      {
        key: str
        value: str
      },
      ...
    ]

    :param config:
    :param _:
    :return:
    """


    # Get key and value
    key = config.get("key", None)
    value = config.get("value", None)

    # Make sure we actually got values
    req_assert(key is not None and  value is not None, message='invalid config')

    # Find config item in db
    db_item = Config.query.filter(Config.key == key).first()

    # Create the item if it didn't exist
    if db_item is None:
        db_item = Config(key=key, value=value)

    # Update the value
    db_item.value = value
    db.session.add(db_item)

    # Commit the changes
    db.session.commit()

    items = Config.query.all()
    return success_response(
        {
            "config": [item.data for item in items],
            "status": "Config saved",
        }
    )
