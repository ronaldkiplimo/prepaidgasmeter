from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "phone_number", "first_name", "last_name",
            "national_id", "role", "is_verified", "email_verified", "mfa_enabled",
            "is_staff", "is_active", "created_at",
        )
        read_only_fields = ("id", "is_verified", "email_verified", "is_staff", "is_active", "created_at")


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("role", "is_active")

    def validate(self, attrs):
        request = self.context.get("request")
        target = self.instance
        if target and request and target.pk == request.user.pk and attrs.get("is_active") is False:
            raise serializers.ValidationError({"is_active": "Admins cannot deactivate their own account."})
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.CUSTOMER)

    class Meta:
        model = User
        fields = (
            "username", "email", "phone_number", "password", "password_confirm",
            "first_name", "last_name", "national_id", "role",
        )

    def validate_phone_number(self, value):
        normalized = value.strip().replace(" ", "")
        if normalized.startswith("0"):
            normalized = "254" + normalized[1:]
        elif normalized.startswith("+"):
            normalized = normalized[1:]
        return normalized

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        role = attrs.get("role", User.Role.CUSTOMER)
        if role == User.Role.ADMIN:
            raise serializers.ValidationError({"role": "Cannot self-register as admin."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "national_id")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        return attrs
