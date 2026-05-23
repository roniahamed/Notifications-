from django.db import models
from django.conf import settings


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    PERMANENTLY_FAILED = "PERMANENTLY_FAILED", "Permanently Failed"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )
    retry_count = models.PositiveSmallIntegerField(default=0)
    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "notifications"
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.title} – {self.user.email}"

    @property
    def is_retryable(self):
        return self.status == NotificationStatus.FAILED and self.retry_count < 3

    @property
    def max_retries_reached(self):
        return self.retry_count >= 3
