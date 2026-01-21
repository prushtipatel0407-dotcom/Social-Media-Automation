from celery import shared_task
from .utils import send_email

@shared_task
def send_email_task(subject, message, recipients):
    send_email(subject, message, recipients)
