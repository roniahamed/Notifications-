from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "status", "retry_count", "scheduled_time", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "user__email")
    readonly_fields = ("celery_task_id", "retry_count", "created_at", "updated_at")
    ordering = ("-created_at",)
