from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync

celery_app = Celery()
celery_app.config_from_object("src.config")


@celery_app.task()
def send_email(
    recipients: list[str],
    subject: str,
    body: str = None,
    context: dict = None,
    template_name: str = None,
):
    message = create_message(
        recipients=recipients, subject=subject, body=body, context=context
    )
    if template_name:
        async_to_sync(mail.send_message)(message, template_name=template_name)
    else:
        async_to_sync(mail.send_message)(message)