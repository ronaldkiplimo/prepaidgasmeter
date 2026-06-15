from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "channel",
            "notification_type",
            "recipient",
            "subject",
            "message",
            "status",
            "sent_at",
            "created_at",
        )
