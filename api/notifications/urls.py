from django.urls import path
from .views import (
    CreateNotificationView,
    NotificationListView,
    NotificationDetailView,
    RetryNotificationView,
)

urlpatterns = [
    path("", CreateNotificationView.as_view(), name="notification-create"),
    path("history/", NotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("<int:pk>/retry/", RetryNotificationView.as_view(), name="notification-retry"),
]
