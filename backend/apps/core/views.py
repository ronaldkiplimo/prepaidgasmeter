from drf_spectacular.utils import extend_schema
from rest_framework import permissions, views
from rest_framework.response import Response

from apps.core.config_check import integration_status
from apps.core.permissions import IsAdminRole


class IntegrationStatusView(views.APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(tags=["System"], summary="Check M-Pesa and Stron configuration status")
    def get(self, request):
        return Response(integration_status())
