from datetime import datetime

from dateutil import tz

America_New_York = tz.gettz('America/New_York')


def convert_to_local(dt: datetime) -> datetime:
    return dt.astimezone(America_New_York).replace(tzinfo=None)
