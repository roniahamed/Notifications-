import logging
from celery import shared_task
from .services import generate_otp, store_otp, send_otp_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_verification_email_task(self, email):
    try:
        otp = generate_otp()
        store_otp(email, otp)
        send_otp_email(email, otp)
        logger.info(f"OTP sent to {email}")
    except Exception as exc:
        logger.error(f"OTP email failed for {email}: {exc}")
        raise self.retry(exc=exc)
