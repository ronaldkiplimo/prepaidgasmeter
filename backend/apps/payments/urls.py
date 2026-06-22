from django.urls import path

from .views import (
    AdminTransactionListView,
    MeterLookupView,
    MpesaCallbackView,
    PurchaseTokenView,
    TransactionDetailView,
    TransactionListView,
    VendingPreviewView,
)

urlpatterns = [
    path("preview/", VendingPreviewView.as_view(), name="vending-preview"),
    path("purchase/", PurchaseTokenView.as_view(), name="purchase-token"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("transactions/<str:reference>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa-callback"),
    path("admin/transactions/", AdminTransactionListView.as_view(), name="admin-transactions"),
    path("meters/<str:meter_number>/lookup/", MeterLookupView.as_view(), name="meter-lookup"),
]
