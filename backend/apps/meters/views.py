from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.audit.services import log_audit
from .models import Meter
from .serializers import MeterListSerializer, MeterSerializer


@extend_schema_view(
    list=extend_schema(tags=["Meters"], summary="List user meters"),
    create=extend_schema(tags=["Meters"], summary="Add a new meter"),
    retrieve=extend_schema(tags=["Meters"], summary="Get meter details"),
    update=extend_schema(tags=["Meters"], summary="Update meter"),
    partial_update=extend_schema(tags=["Meters"], summary="Partially update meter"),
    destroy=extend_schema(tags=["Meters"], summary="Remove meter"),
)
class MeterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meter.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == "list":
            return MeterListSerializer
        return MeterSerializer

    def perform_create(self, serializer):
        meter = serializer.save()
        log_audit(
            user=self.request.user,
            action="METER_ADDED",
            resource_type="Meter",
            resource_id=str(meter.id),
            details={"meter_number": meter.meter_number},
            ip_address=self._get_ip(),
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        log_audit(
            user=self.request.user,
            action="METER_REMOVED",
            resource_type="Meter",
            resource_id=str(instance.id),
            ip_address=self._get_ip(),
        )

    def _get_ip(self):
        request = self.request
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
