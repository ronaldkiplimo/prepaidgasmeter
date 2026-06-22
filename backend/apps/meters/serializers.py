from rest_framework import serializers

from .models import Meter, MeterReading


class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = (
            "id", "meter_number", "meter_serial", "stron_customer_id", "customer_name",
            "phone_number", "account_number", "nickname", "meter_type", "location", "estate",
            "status", "valve_status", "tamper_status", "current_credit", "current_balance",
            "installation_date", "last_vending_date", "is_active", "is_primary",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "current_credit", "current_balance", "last_vending_date",
            "created_at", "updated_at",
        )

    def validate_meter_number(self, value):
        normalized = value.strip().upper()
        if len(normalized) < 6:
            raise serializers.ValidationError("Meter number must be at least 6 characters.")
        return normalized

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        if not validated_data.get("customer_name"):
            validated_data["customer_name"] = self.context["request"].user.display_name
        if not validated_data.get("phone_number"):
            validated_data["phone_number"] = self.context["request"].user.phone_number
        return super().create(validated_data)


class MeterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = (
            "id", "meter_number", "nickname", "meter_type", "status",
            "current_credit", "current_balance", "valve_status", "tamper_status",
            "is_active", "is_primary",
        )


class MeterReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterReading
        fields = (
            "id", "reading_date", "units_consumed", "credit_remaining",
            "balance_remaining", "source", "created_at",
        )
