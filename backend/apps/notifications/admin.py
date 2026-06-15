from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "channel", "notification_type", "status", "created_at")
    list_filter = ("channel", "status", "notification_type")
    search_fields = ("recipient", "message")
