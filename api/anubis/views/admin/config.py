from flask import Blueprint

from anubis.models import db, Config
from anubis.utils.auth.http import require_admin, require_superuser
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http import success_response

config_ = Blueprint("config", __name__, url_prefix="/admin/config")


@config_.route("/list")
@require_admin()
@json_response
def config_list():
    """
    List all config items.

    :return:
    """

    # Pull all the config items
    items = Config.query.all()

    # Return the broken down objects
    return success_response({"config": [item.data for item in items]})


@config_.route("/save", methods=["POST"])
@require_superuser()
@json_endpoint(required_fields=[("config", list)])
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

    # Iterate over all config items
    for item in config:

        # Get key and value
        key = item.get("key", None)
        value = item.get("value", None)

        # Make sure we actually got values
        if key is None or value is None:
            continue

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
