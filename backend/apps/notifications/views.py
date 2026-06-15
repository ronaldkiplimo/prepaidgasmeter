from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(tags=["Notifications"], summary="List user notifications")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
