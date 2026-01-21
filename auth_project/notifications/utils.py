import random
from django.core.cache import cache

OTP_TTL = 300        # 5 minutes
RATE_LIMIT_TTL = 60 # 1 minute

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
