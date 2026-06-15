from rest_framework import serializers

from .models import Meter


class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = (
            "id",
            "meter_number",
            "account_number",
            "nickname",
            "meter_type",
            "utility_provider",
            "location",
            "is_active",
            "is_primary",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_meter_number(self, value):
        normalized = value.strip().upper()
        if len(normalized) < 6:
            raise serializers.ValidationError("Meter number must be at least 6 characters.")
        return normalized

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class MeterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = (
            "id",
            "meter_number",
            "nickname",
            "meter_type",
            "is_active",
            "is_primary",
        )
