import traceback

import jinja2
from googleapiclient.errors import Error
from datetime import datetime
from anubis.constants import EMAIL_FROM
from anubis.utils.google.gmail import send_message
from anubis.models import db, User, EmailTemplate, EmailEvent
from anubis.utils.email.smtp import create_message
from anubis.utils.logging import logger
from anubis.utils.config import get_config_str
from anubis.utils.auth.admin import get_admin_user


def send_email_event_admin(
    reference_id: str,
    reference_type: str,
    template_key: str,
    context: dict,
):
    # Get admin user
    user = get_admin_user()

    # Limit message to one per hour
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    # Send email event
    send_email_event(
        user,
        reference_id=f'{reference_id} {now}',
        reference_type=reference_type,
        template_key=template_key,
        context=context,
    )


def send_email_event(
    user: User,
    reference_id: str,
    reference_type: str,
    template_key: str,
    context: dict,
) -> EmailEvent | None:
    event: EmailEvent | None = EmailEvent.query.filter(
        EmailEvent.owner_id == user.id,
        EmailEvent.reference_id == reference_id,
        EmailEvent.reference_type == reference_type,
    ).first()

    # If event already sent, then skip
    if event is not None:
        logger.debug(f'Email already sent. '
                     f'Skipping user_id={user.id} reference_id={reference_id} reference_type={reference_type}')
        return event

    email_template: EmailTemplate | None = EmailTemplate.query.filter(EmailTemplate.key == template_key).first()
    if email_template is None:
        logger.error(f'Email template not found. Aborting sending email template_key={template_key}')
        return

    # Build templates
    subject_template = jinja2.Template(email_template.subject)
    body_template = jinja2.Template(email_template.body)

    # Render templates
    subject = subject_template.render(**context)
    body = body_template.render(**context)

    # Create email message
    message = create_message(
        EMAIL_FROM,
        user.netid + '@nyu.edu',
        subject,
        body,
    )

    # Send email
    try:
        success = send_message(message) is not False
        # logger.info(f'Sent email {message}')
    except Error as e:
        logger.error(f'Failed to send email!\nerror={e}\n\n{traceback.format_exc()}\nemail={message}')
        return

    if success:
        event: EmailEvent = EmailEvent(
            owner_id=user.id,
            template_id=template_key,
            reference_id=reference_id,
            reference_type=reference_type,
            subject=subject,
            body=body,
        )
        db.session.add(event)
        db.session.commit()
