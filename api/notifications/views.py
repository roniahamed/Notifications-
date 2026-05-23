import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Notification, NotificationStatus
from .serializers import (
    NotificationCreateSerializer,
    NotificationListSerializer,
    NotificationDetailSerializer,
)
from .paginations import NotificationPagination
from .tasks import send_notification_task

logger = logging.getLogger(__name__)


class CreateNotificationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationCreateSerializer

    def post(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save(user=request.user, status=NotificationStatus.PENDING)

        # Schedule Celery task with eta
        eta = notification.scheduled_time
        task = send_notification_task.apply_async(
            args=[notification.id],
            eta=eta,
        )
        notification.celery_task_id = task.id
        notification.save(update_fields=["celery_task_id"])

        logger.info(f"Notification {notification.id} scheduled at {eta} for user {request.user.email}")
        return Response(
            NotificationDetailSerializer(notification).data,
            status=status.HTTP_201_CREATED,
        )


class NotificationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationListSerializer
    pagination_class = NotificationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["title", "message"]
    ordering_fields = ["scheduled_time", "created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationDetailSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)


class RetryNotificationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    from drf_spectacular.utils import extend_schema
    @extend_schema(request=None, responses={200: NotificationDetailSerializer})
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        if notification.status == NotificationStatus.SENT:
            return Response({"detail": "Notification already sent."}, status=status.HTTP_400_BAD_REQUEST)

        if notification.status == NotificationStatus.PERMANENTLY_FAILED:
            return Response(
                {"detail": "Notification permanently failed. Cannot retry."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if notification.status == NotificationStatus.PENDING:
            return Response({"detail": "Notification is still pending."}, status=status.HTTP_400_BAD_REQUEST)

        if notification.retry_count >= 3:
            notification.status = NotificationStatus.PERMANENTLY_FAILED
            notification.save(update_fields=["status", "updated_at"])
            return Response(
                {"detail": "Max retries reached. Marked as permanently failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset status and schedule immediately
        notification.status = NotificationStatus.PENDING
        notification.scheduled_time = timezone.now()
        notification.save(update_fields=["status", "scheduled_time", "updated_at"])

        task = send_notification_task.apply_async(args=[notification.id])
        notification.celery_task_id = task.id
        notification.save(update_fields=["celery_task_id"])

        logger.info(f"Notification {notification.id} manually retried by user {request.user.email}")
        return Response(
            NotificationDetailSerializer(notification).data,
            status=status.HTTP_200_OK,
        )
