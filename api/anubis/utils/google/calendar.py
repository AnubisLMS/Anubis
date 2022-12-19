import json
import traceback

import googleapiclient.discovery

from anubis.utils.data import is_debug
from anubis.utils.logging import logger
from anubis.utils.google.service import build_google_service
from anubis.constants import GOOGLE_CALENDAR_SCOPES, GOOGLE_CALENDAR_CREDS_SECRET


def get_calendar_service() -> googleapiclient.discovery.Resource:
    return build_google_service(
        GOOGLE_CALENDAR_CREDS_SECRET,
        'calendar',
        'v3',
        GOOGLE_CALENDAR_SCOPES
    )


def add_calendar(
    calendar: dict
) -> str:
    """Add a secondary calendar.

    Args:
      calendar: The calendar to be added

    Returns:
      The identifier of the added calendar
    """

    service = get_calendar_service()

    logger.debug(f"ADDING CALENDAR {json.dumps(calendar)}")

    try:
        calendar = service.calendars().insert(body=calendar).execute()
        return calendar['id']
    except Exception as e:
        logger.error(traceback.format_exc())
        if raise_:
            raise e
        return False


def delete_calendar(
    calendar_id: str
) -> str:
    """Delete a secondary calendar.

    Args:
      calendar_id: The calendar to be deleted

    Returns:
      The identifier of the deleted calendar
    """

    service = get_calendar_service()

    logger.debug(f"DELETING CALENDAR {calendar_id}")

    try:
        service.calendars().delete(calendarId=calendar_id).execute()
        return calendar['id']
    except Exception as e:
        logger.error(traceback.format_exc())
        if raise_:
            raise e
        return False


def add_event(
    calendar_id: str="primary",
    event: dict,
) -> str:
    """Add a Google Calendar event.

    Args:
      calendar_id: The calendarId to which the event will be added
      event:       The event to be added

    Returns:
      The identifier of the added event
    """

    service = get_calendar_service()

    logger.debug(f"ADDING CALENDAR EVENT {json.dumps(event)}")

    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return event.get('id')
    except Exception as e:
        logger.error(traceback.format_exc())
        if raise_:
            raise e
        return False


def delete_event(
    calendar_id: str="primary",
    event_id: str,
) -> str:
    """Delete a Google Calendar event.

    Args:
      calendar_id: The calendarId to which the event will be deleted
      event_id:       The event to be deleted

    Returns:
      The identifier of the deleted event
    """

    service = get_calendar_service()

    logger.debug(f"DELETING CALENDAR EVENT {event_id} in {calendar_id}")

    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return event_id
    except Exception as e:
        logger.error(traceback.format_exc())
        if raise_:
            raise e
        return False
