from datetime import datetime, timedelta

from anubis.models import TheiaSession
from anubis.utils.config import get_config_int


def get_active_theia_sessions() -> list[TheiaSession]:
    theia_active_minutes_window: int = get_config_int('THEIA_ACTIVE_MINUTES_WINDOW', default=15)

    # Get all theia sessions within the last 10 minutes that are
    # active and don't have cluster_address
    theia_sessions: list[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.created > datetime.now() - timedelta(minutes=theia_active_minutes_window),
    ).all()

    return theia_sessions
