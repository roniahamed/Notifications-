from django.utils import timezone
from rest_framework import serializers
from .models import Notification


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "title", "message", "scheduled_time")

    def validate_scheduled_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "scheduled_time",
            "status",
            "retry_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class NotificationDetailSerializer(NotificationListSerializer):
    pass
