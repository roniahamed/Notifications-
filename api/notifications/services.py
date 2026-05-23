import logging
from django.core.mail import send_mail
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def send_email_notification(user_email, title, message):
    subject = f"Notification: {title}"
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
        logger.info(f"Email notification sent to {user_email}")
    except Exception as e:
        logger.error(f"Email notification failed for {user_email}: {e}")
        raise


def send_websocket_notification(user_id, notification_id, title, message):
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification.message",
                "notification_id": notification_id,
                "title": title,
                "message": message,
            },
        )
        logger.info(f"WebSocket notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket notification failed for user {user_id}: {e}")


def send_fcm_notification(fcm_token, title, message):
    if not fcm_token:
        return
    try:
        import firebase_admin
        from firebase_admin import messaging, credentials


        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)

        msg = messaging.Message(
            notification=messaging.Notification(title=title, body=message),
            token=fcm_token,
        )
        response = messaging.send(msg)
        logger.info(f"FCM notification sent: {response}")
    except Exception as e:
        logger.error(f"FCM notification failed: {e}")

