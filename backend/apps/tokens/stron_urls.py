from django.urls import path

from .stron_views import StronClearCreditView, StronClearTamperView

urlpatterns = [
    path("clear-credit/", StronClearCreditView.as_view(), name="stron-clear-credit"),
    path("clear-tamper/", StronClearTamperView.as_view(), name="stron-clear-tamper"),
]
