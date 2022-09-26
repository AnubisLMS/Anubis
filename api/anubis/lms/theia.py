from datetime import datetime, timedelta

from anubis.models import TheiaSession


def get_active_theia_sessions() -> list[TheiaSession]:
    # Get all theia sessions within the last 10 minutes that are
    # active and don't have cluster_address
    theia_sessions: list[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.cluster_address == None,
        TheiaSession.created > datetime.now() - timedelta(minutes=10),
    ).all()

    return theia_sessions
