import random
import string
import logging
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

logger = logging.getLogger(__name__)
User = get_user_model()

OTP_CACHE_PREFIX = "otp:"
RESET_TOKEN_PREFIX = "pwd_reset:"


def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))


def store_otp(email, otp):
    key = f"{OTP_CACHE_PREFIX}{email}"
    hashed_otp = make_password(otp)
    cache.set(key, hashed_otp, timeout=settings.OTP_EXPIRE_SECONDS)


def verify_otp(email, otp):
    key = f"{OTP_CACHE_PREFIX}{email}"
    stored_hash = cache.get(key)
    if stored_hash and check_password(otp, stored_hash):
        cache.delete(key)
        return True
    return False


def send_otp_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your OTP is: {otp}\nIt expires in {settings.OTP_EXPIRE_SECONDS // 60} minutes."
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        raise


def store_reset_token(email, token):
    key = f"{RESET_TOKEN_PREFIX}{token}"
    cache.set(key, email, timeout=settings.OTP_EXPIRE_SECONDS)


def verify_reset_token(token):
    key = f"{RESET_TOKEN_PREFIX}{token}"
    email = cache.get(key)
    if email:
        cache.delete(key)
    return email


def send_password_reset_email(email, token):
    subject = "Password Reset Request"
    message = f"Use this token to reset your password: {token}\nExpires in {settings.OTP_EXPIRE_SECONDS // 60} minutes."
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        raise
