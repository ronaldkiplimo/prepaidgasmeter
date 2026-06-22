from django.contrib import admin

from .models import Meter


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ("meter_number", "user", "nickname", "meter_type", "status", "is_active", "is_primary")
    list_filter = ("meter_type", "status", "valve_status", "is_active", "is_primary")
    search_fields = ("meter_number", "account_number", "user__phone_number", "nickname")
    raw_id_fields = ("user",)
