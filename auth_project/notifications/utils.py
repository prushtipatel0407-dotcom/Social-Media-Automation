import random
import time

OTP_STORE = {}
OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp():
    return str(random.randint(100000, 999999))


def store_otp(email, otp):
    OTP_STORE[email] = {
        "otp": otp,
        "timestamp": time.time()
    }


def verify_otp(email, otp):
    data = OTP_STORE.get(email)

    if not data:
        return False, "OTP not found"

    if time.time() - data["timestamp"] > OTP_EXPIRY_SECONDS:
        del OTP_STORE[email]
        return False, "OTP expired"

    if data["otp"] != otp:
        return False, "Invalid OTP"

    del OTP_STORE[email]
    return True, "OTP verified"