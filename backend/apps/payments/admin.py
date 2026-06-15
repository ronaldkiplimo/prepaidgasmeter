from django.contrib import admin

from .models import Payment, Transaction


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("checkout_request_id", "mpesa_receipt_number", "status")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "meter", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("reference", "user__phone_number", "meter__meter_number")
    readonly_fields = ("reference", "created_at", "updated_at", "completed_at")
    inlines = [PaymentInline]
    date_hierarchy = "created_at"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "method", "status", "amount", "mpesa_receipt_number")
    list_filter = ("status", "method")
    search_fields = ("checkout_request_id", "mpesa_receipt_number", "phone_number")
