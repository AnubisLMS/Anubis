import json
import traceback

import googleapiclient.discovery

from anubis.utils.data import is_debug
from anubis.utils.logging import logger
from anubis.utils.config import get_config_bool
from anubis.utils.google.service import build_google_service
from anubis.constants import GOOGLE_CALENDAR_SCOPES, GOOGLE_CALENDAR_CREDS_SECRET


def get_calendar_service() -> googleapiclient.discovery.Resource:
    return build_google_service(
        GOOGLE_CALENDAR_CREDS_SECRET,
        'calendar',
        'v3',
        GOOGLE_CALENDAR_SCOPES
    )


def add_event(
    calendar_id: str="primary",
    event: dict,
) -> str:
    """Add a Google Calendar event.

    Args:
      calendar_id: The calendarId to which the event is added
      event:       The event to be added

    Returns:
      Link to the added event.
    """

    service = get_calendar_service()

    logger.debug(f"ADDING CALENDAR EVENT {json.dumps(event)}")

    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return event.get('htmlLink')
    except Exception as e:
        logger.error(traceback.format_exc())
        if raise_:
            raise e
        return False
