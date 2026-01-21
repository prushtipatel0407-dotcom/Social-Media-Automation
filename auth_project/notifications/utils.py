import random
from django.core.cache import cache

OTP_TTL = 300        # 5 minutes
RATE_LIMIT_TTL = 60 # 1 minute
from django.core.mail import send_mail
from django.conf import settings

def send_reset_email(user, token):
    reset_link = (
        "http://127.0.0.1:8000"
        "/static/reset-password/reset-password.html"
        f"?token={token}"
    )

    subject = "Reset Your Password"
    message = f"""
Hi {user.email},

Click the link below to reset your password:

{reset_link}

This link is valid for 15 minutes.
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

    print("RESET LINK:", reset_link)


def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp(email, otp):
    cache.set(f"otp:{email}", otp, timeout=OTP_TTL)

def can_send_otp(email):
    key = f"otp_limit:{email}"
    if cache.get(key):
        return False
    cache.set(key, True, timeout=RATE_LIMIT_TTL)
    return True

def verify_otp(email, otp):
    saved = cache.get(f"otp:{email}")
    if not saved:
        return False, "OTP expired"

    if saved != otp:
        return False, "Invalid OTP"

    cache.delete(f"otp:{email}")
    return True, "OTP verified"
