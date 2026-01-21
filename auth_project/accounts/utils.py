import random
import uuid
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

OTP_TTL = 300  # 5 min
OTP_RATE_LIMIT = 60  # 1 min
RESET_TTL = 900  # 15 min
RESET_RATE_LIMIT = 60

def generate_otp():
    return str(random.randint(100000, 999999))

def can_send_otp(email):
    key = f"otp_limit:{email}"
    if cache.get(key):
        return False
    cache.set(key, True, timeout=OTP_RATE_LIMIT)
    return True

def store_otp(email, otp):
    cache.set(f"otp:{email}", otp, timeout=OTP_TTL)

def verify_otp(email, otp):
    saved = cache.get(f"otp:{email}")
    if not saved:
        return False, "OTP expired"
    if saved != otp:
        return False, "Invalid OTP"
    cache.delete(f"otp:{email}")
    return True, "OTP verified"

# ---------------------------
# Password Reset
# ---------------------------
def can_request_reset(email):
    key = f"reset_limit:{email}"
    if cache.get(key):
        return False
    cache.set(key, True, timeout=RESET_RATE_LIMIT)
    return True

def create_reset_token(email):
    token = uuid.uuid4().hex
    cache.set(f"reset:{token}", email, timeout=RESET_TTL)
    return token

def verify_reset_token(token):
    email = cache.get(f"reset:{token}")
    if email:
        cache.delete(f"reset:{token}")
    return email

def send_email(subject, message, recipients):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipients,
        fail_silently=False
    )
