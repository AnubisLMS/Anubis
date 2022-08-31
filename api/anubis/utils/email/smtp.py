import base64
import io
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from anubis.utils.http.files import get_mime_type


def create_message(sender: str, to: str, subject: str, message_text: str) -> dict[str, str]:
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart("mixed")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    alt = MIMEMultipart("alternative")
    plain = MIMEText(message_text, "plain")
    alt.attach(plain)

    rel = MIMEMultipart("related")
    html = MIMEText(message_text, "html")
    rel.attach(html)

    alt.attach(rel)

    message.attach(alt)
    return {"raw": base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def create_message_with_attachment(
    sender: str,
    to: str,
    subject: str,
    message_text: str,
    file: io.BytesIO,
    filename: str,
) -> dict[str, str]:
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.
      filename: The name of the file to be attached to the message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type = get_mime_type(file.read())
    file.seek(0)

    if content_type is None:
        content_type = "application/octet-stream"

    main_type, sub_type = content_type.split("/", 1)
    if main_type == "text":
        msg = MIMEText(file.read().decode("utf-8", errors="ignore"), _subtype=sub_type)
    elif main_type == "image":
        msg = MIMEImage(file.read(), _subtype=sub_type)
    elif main_type == "audio":
        msg = MIMEAudio(file.read(), _subtype=sub_type)
    else:
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(file.read())

    msg.add_header("Content-Disposition", "attachment", filename=filename)
    message.attach(msg)

    return {"raw": base64.urlsafe_b64encode(message.as_string().encode()).decode()}
