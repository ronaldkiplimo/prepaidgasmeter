from django.urls import path

from apps.core.views import IntegrationStatusView

urlpatterns = [
    path("integrations/", IntegrationStatusView.as_view(), name="integration-status"),
]
