from datetime import datetime, timedelta

from flask import Blueprint

from anubis.models import db, EmailEvent, EmailTemplate
from anubis.utils.auth.http import require_superuser
from anubis.utils.http import success_response, error_response
from anubis.utils.http.decorators import json_endpoint, json_response

email_ = Blueprint("email", __name__, url_prefix="/super/email")


def get_all_templates(extra: dict = None):
    extra = extra or dict()
    templates: list[EmailTemplate] = EmailTemplate.query.all()
    return success_response({
        'templates': [
            template.data for template in templates
        ],
        **extra
    })


@email_.get("/template/list")
@require_superuser()
@json_response
def super_email_template_list():
    return get_all_templates()


@email_.post("/template/save")
@require_superuser()
@json_endpoint([('key', str), ('subject', str), ('body', str)])
def super_email_template_save(key: str, subject: str, body: str):
    template: EmailTemplate | None = EmailTemplate.query.filter(
        EmailTemplate.key == key
    ).first()

    template.subject = subject
    template.body = body

    db.session.add(template)
    db.session.commit()

    return get_all_templates({
        'variant': 'success',
        'status':  'Template saved'
    })


@email_.post("/template/new")
@require_superuser()
@json_endpoint([('key', str)])
def super_email_template_new(key: str):
    if key == '':
        return error_response('Key empty')

    template: EmailTemplate = EmailTemplate(
        key=key,
        subject='',
        body='',
    )

    db.session.add(template)
    db.session.commit()

    return get_all_templates({
        'variant': 'success',
        'status':  'Template created'
    })


@email_.post("/template/delete")
@require_superuser()
@json_endpoint([('key', str)])
def super_email_template_delete(key: str):
    if key == '':
        return error_response('Key empty')

    EmailTemplate.query.filter(
        EmailTemplate.key == key
    ).delete()
    db.session.commit()

    return get_all_templates({
        'variant': 'warning',
        'status':  'Template Deleted'
    })


@email_.get("/event/list")
@require_superuser()
@json_response
def super_email_event_list():
    events: list[EmailEvent] = EmailEvent.query.filter(
        EmailEvent.created > datetime.now() - timedelta(days=1)
    ).all()

    return success_response({
        'events': [
            event.data for event in events
        ]
    })
