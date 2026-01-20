from django.core.cache import cache
import random
import hashlib
from notifications.tasks import send_email_task

OTP_TTL = 300  # 5 minutes

def generate_otp():
    return str(random.randint(100000, 999999))

def _hash(email, otp):
    return hashlib.sha256(f"{email}:{otp}".encode()).hexdigest()

def send_otp(email, purpose="default"):
    otp = generate_otp()
    key = f"otp:{purpose}:{email}"

    cache.set(key, _hash(email, otp), OTP_TTL)

    send_email_task.delay(
        "Your OTP Code",
        f"Your OTP is {otp}. Valid for 5 minutes.",
        email
    )

def verify_otp(email, otp, purpose="default"):
    key = f"otp:{purpose}:{email}"
    stored = cache.get(key)

    if not stored:
        return False

    if stored == _hash(email, otp):
        cache.delete(key)
        return True

    return False
