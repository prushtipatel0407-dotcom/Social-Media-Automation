import random
import hashlib
from django.core import signing
from django.utils import timezone
from datetime import timedelta

OTP_EXPIRY_MINUTES = 5


def generate_otp():
    return f"{random.randint(100000, 999999)}"


def create_otp_token(email, otp):
    data = {
        "email": email,
        "otp_hash": hashlib.sha256(otp.encode()).hexdigest(),
        "exp": (timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)).timestamp()
    }
    return signing.dumps(data)


def verify_otp_token(token, email, otp):
    try:
        data = signing.loads(token)
    except signing.BadSignature:
        return False, "Invalid token"

    if data["email"] != email:
        return False, "Email mismatch"

    if timezone.now().timestamp() > data["exp"]:
        return False, "OTP expired"

    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    if otp_hash != data["otp_hash"]:
        return False, "Invalid OTP"

    return True, "OTP verified"