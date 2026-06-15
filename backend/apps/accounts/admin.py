from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number", "username", "email", "is_verified", "is_staff", "created_at")
    list_filter = ("is_verified", "is_staff", "is_active")
    search_fields = ("phone_number", "username", "email", "national_id")
    ordering = ("-created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone_number", "national_id", "is_verified")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("phone_number", "national_id")}),
    )
