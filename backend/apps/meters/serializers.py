from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Meter, MeterReading

User = get_user_model()


class MeterSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
    user_phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    user_display_name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = Meter
        fields = (
            "id", "user", "user_phone_number", "user_display_name",
            "meter_number", "meter_serial", "stron_customer_id", "customer_name",
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

        # Ensure meter_number is globally unique (only one user can be assigned a meter)
        qs = Meter.objects.filter(meter_number=normalized)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This meter number is already assigned to a user.")

        return normalized

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        is_admin = bool(
            user
            and user.is_authenticated
            and (user.is_superuser or getattr(user, "role", None) == User.Role.ADMIN)
        )

        if self.instance and "user" in attrs and not is_admin:
            raise serializers.ValidationError({"user": "Only admins can assign meters to users."})

        if self.instance is None and "user" not in attrs:
            raise serializers.ValidationError({"user": "A user must be selected for this meter."})

        return attrs

    def create(self, validated_data):
        assigned_user = validated_data["user"]
        if not validated_data.get("customer_name"):
            validated_data["customer_name"] = assigned_user.display_name
        if not validated_data.get("phone_number"):
            validated_data["phone_number"] = assigned_user.phone_number
        return super().create(validated_data)

    def update(self, instance, validated_data):
        assigned_user = validated_data.get("user")
        if assigned_user and assigned_user != instance.user:
            if not validated_data.get("customer_name"):
                validated_data["customer_name"] = assigned_user.display_name
            if not validated_data.get("phone_number"):
                validated_data["phone_number"] = assigned_user.phone_number
        return super().update(instance, validated_data)


class MeterListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    user_display_name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = Meter
        fields = (
            "id", "user", "user_phone_number", "user_display_name",
            "meter_number", "nickname", "meter_type", "status",
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
