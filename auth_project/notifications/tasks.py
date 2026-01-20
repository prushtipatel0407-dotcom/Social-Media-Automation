from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, to):
    try:
        send_mail(
            subject,
            message,
            None,
            [to],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
