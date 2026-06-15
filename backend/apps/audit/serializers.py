from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone_number", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user_phone",
            "action",
            "resource_type",
            "resource_id",
            "details",
            "ip_address",
            "created_at",
        )
