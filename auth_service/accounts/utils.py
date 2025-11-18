# accounts/utils.py
import secrets
import time
from django.conf import settings

redis_client = settings.REDIS_CLIENT

# OTP settings
OTP_TTL_SECONDS = 300        # 5 minutes
OTP_RESEND_COOLDOWN = 60     # 1 minute
OTP_MAX_ATTEMPTS = 5         # Prevent brute forcing


def generate_otp(n=6):
    """Generate a zero-padded numeric OTP."""
    return str(secrets.randbelow(10 ** n)).zfill(n)


# ---------- Redis key builders ----------
def otp_key(email):
    return f"otp:{email.lower()}"


def otp_attempts_key(email):
    return f"otp_attempts:{email.lower()}"


def otp_last_sent_key(email):
    return f"otp_last_sent:{email.lower()}"


# ---------- Redis operations ----------
def set_otp(email, otp):
    """Store OTP with expiry and track last sent time."""
    redis_client.set(otp_key(email), otp, ex=OTP_TTL_SECONDS)
    redis_client.delete(otp_attempts_key(email))
    redis_client.set(otp_last_sent_key(email), int(time.time()), ex=OTP_TTL_SECONDS)


def get_otp(email):
    """Return OTP string or None if expired / missing."""
    return redis_client.get(otp_key(email))


def increment_attempts(email):
    """Increase failed attempts counter."""
    key = otp_attempts_key(email)
    attempts = redis_client.incr(key)

    # ensure attempts expire same as OTP
    if attempts == 1:
        redis_client.expire(key, OTP_TTL_SECONDS)

    return attempts


def get_attempts(email):
    val = redis_client.get(otp_attempts_key(email))
    return int(val) if val else 0


def can_resend(email):
    last = redis_client.get(otp_last_sent_key(email))
    if not last:
        return True
    return (int(time.time()) - int(last)) >= OTP_RESEND_COOLDOWN


def revoke_otp(email):
    """Delete OTP and attempts."""
    redis_client.delete(otp_key(email))
    redis_client.delete(otp_attempts_key(email))
    redis_client.delete(otp_last_sent_key(email))
