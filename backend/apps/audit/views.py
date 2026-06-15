from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = AuditLog.objects.select_related("user").all()
    filterset_fields = ["action", "resource_type"]
    search_fields = ["action", "resource_id", "user__phone_number"]

    @extend_schema(tags=["Admin"], summary="Admin: list audit logs")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
