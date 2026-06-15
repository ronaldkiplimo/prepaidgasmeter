from django.contrib import admin

from .models import ElectricityToken


@admin.register(ElectricityToken)
class ElectricityTokenAdmin(admin.ModelAdmin):
    list_display = ("meter_number", "token_units", "token_amount", "status", "generated_at")
    list_filter = ("status",)
    search_fields = ("meter_number", "token", "stron_receipt_number")
    readonly_fields = ("token", "generated_at", "delivered_at")
