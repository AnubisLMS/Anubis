import traceback
from datetime import datetime

import requests

from anubis.env import env
from anubis.models import EmailEvent, db
from anubis.utils.auth.admin import get_admin_user
from anubis.utils.hash import sha256
from anubis.utils.logging import logger
from anubis.utils.redis import create_redis_lock


def send_webhook(content: str):
    """
    Send webhook via url specified in environment
    """

    # Get discord webhook
    webhook_url = env.DISCORD_WEBHOOK

    # Check that webhook is valid
    if webhook_url is None:
        logger.warning(f'Skipping sending discord message, webhook url not defined.')
        return

    # Get admin user
    user = get_admin_user()

    # Create reference unique to the hour
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    reference_id = sha256(content + str(now))[:36]

    # Create distributed lock for the hour (release in 3.0 seconds)
    lock = create_redis_lock(reference_id, auto_release_time=3.0)
    if not lock.acquire(blocking=False):
        return

    # Get event
    event: EmailEvent = EmailEvent.query.filter(
        EmailEvent.owner_id == user.id,
        EmailEvent.reference_id == reference_id,
        EmailEvent.reference_type == 'discord',
    ).first()

    # If event already sent, then skip
    if event is not None:
        return

    # Send actual webhook
    # https://discord.com/developers/docs/resources/webhook#execute-webhook
    try:
        requests.post(
            webhook_url,
            headers={'Content-Type': 'application/json'},
            json={
                'content':    content,
                'username':   'Anubis',
                'avatar_url': 'https://anubis-lms.io/logo512.png',
            },
            timeout=1.0
        )
    except:
        logger.error(traceback.format_exc())
        return

    # Log Event
    event = EmailEvent(
        owner_id=user.id,
        template_id=None,
        reference_id=reference_id,
        reference_type='discord',
        subject='',
        body=content,
    )
    db.session.add(event)
    db.session.commit()

    # Release lock
    lock.release()


if __name__ == '__main__':
    from anubis.app import create_app
    app = create_app()
    with app.app_context():
        with app.test_request_context():
            send_webhook(f"Scaleup triggered by IDE use")