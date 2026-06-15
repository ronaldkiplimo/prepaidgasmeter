from django.urls import path

from apps.payments.views import PurchaseTokenView, TransactionDetailView, TransactionListView
from apps.tokens.views import TokenHistoryView

urlpatterns = [
    path("purchase/", PurchaseTokenView.as_view(), name="token-purchase"),
    path("history/", TokenHistoryView.as_view(), name="token-history"),
    path("transactions/", TransactionListView.as_view(), name="token-transactions"),
    path("transactions/<str:reference>/", TransactionDetailView.as_view(), name="token-transaction-detail"),
]
