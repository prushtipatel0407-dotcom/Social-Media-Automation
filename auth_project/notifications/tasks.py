from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True, max_retries=3)
def send_otp_email_task(self, email, otp):
    try:
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is {otp}. Valid for 5 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
