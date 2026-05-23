import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@shared_task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=60)
def send_notification_task(self, notification_id):
    from .models import Notification, NotificationStatus
    from .services import send_email_notification, send_websocket_notification, send_fcm_notification

    try:
        notification = Notification.objects.select_related("user").get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found.")
        return

    # Skip if already handled (idempotency guard)
    if notification.status in (NotificationStatus.SENT, NotificationStatus.PERMANENTLY_FAILED):
        return

    user = notification.user

    try:
        # Primary channel: email (failure triggers retry)
        send_email_notification(user.email, notification.title, notification.message)

        # Secondary channels: best-effort
        send_websocket_notification(user.id, notification.id, notification.title, notification.message)
        send_fcm_notification(user.fcm_token, notification.title, notification.message)

        notification.status = NotificationStatus.SENT
        notification.save(update_fields=["status", "updated_at"])
        logger.info(f"Notification {notification_id} sent successfully.")

    except Exception as exc:
        notification.retry_count += 1
        logger.warning(f"Notification {notification_id} failed (attempt {notification.retry_count}): {exc}")

        if notification.retry_count >= MAX_RETRIES:
            notification.status = NotificationStatus.PERMANENTLY_FAILED
            notification.save(update_fields=["status", "retry_count", "updated_at"])
            logger.error(f"Notification {notification_id} permanently failed after {MAX_RETRIES} attempts.")
            return

        notification.status = NotificationStatus.FAILED
        notification.save(update_fields=["status", "retry_count", "updated_at"])

        # Exponential backoff: 60s, 120s, 240s
        countdown = 60 * (2 ** (notification.retry_count - 1))
        raise self.retry(exc=exc, countdown=countdown)
