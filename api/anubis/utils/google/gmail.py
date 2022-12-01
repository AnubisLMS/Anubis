import json
import traceback

import googleapiclient.discovery

from anubis.utils.data import is_debug
from anubis.utils.logging import logger
from anubis.utils.config import get_config_bool
from anubis.utils.google.service import build_google_service
from anubis.constants import GOOGLE_GMAIL_CREDS_SCOPES, GOOGLE_GMAIL_CREDS_SECRET


def get_gmail_service() -> googleapiclient.discovery.Resource:
    return build_google_service(
        GOOGLE_GMAIL_CREDS_SECRET,
        'gmail',
        'v1',
        GOOGLE_GMAIL_CREDS_SCOPES
    )


def send_message(
    message: dict[str, str],
    user_id="me",
    force: bool = False,
    raise_: bool = False,
):
    """Send an email message.

    Args:
      message: Message to be sent.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.

    Returns:
      Sent Message.
    """

    service = get_gmail_service()

    email_send_enabled: bool = get_config_bool('EMAIL_SEND_ENABLED', default=False)

    logger.debug(f"SENDING EMAIL {json.dumps(message)}")
    if not force and is_debug() and not email_send_enabled:
        logger.info(f'Email send disabled, skipping '
                    f'debug={is_debug()} email_send_enabled={email_send_enabled}')
        return

    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        return message
    except Exception as e:
        logger.error(traceback.format_exc())
        if raise_:
            raise e
        return False
