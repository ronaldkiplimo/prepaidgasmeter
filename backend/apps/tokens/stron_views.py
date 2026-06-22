from rest_framework import permissions, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.core.permissions import IsAdminRole
from apps.tokens.services.stron import StronAPIError, StronVendingService


class StronClearCreditView(views.APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(tags=["Stron Admin"], summary="Clear meter credit (admin)")
    def post(self, request):
        meter_id = request.data.get("meter_id")
        customer_id = request.data.get("customer_id", "")
        if not meter_id:
            return Response({"detail": "meter_id required"}, status=400)
        try:
            result = StronVendingService().clear_credit(meter_id, customer_id)
            return Response({"result": result})
        except StronAPIError as exc:
            return Response({"detail": str(exc)}, status=400)


class StronClearTamperView(views.APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(tags=["Stron Admin"], summary="Clear tamper lock (admin)")
    def post(self, request):
        meter_id = request.data.get("meter_id")
        customer_id = request.data.get("customer_id", "")
        if not meter_id:
            return Response({"detail": "meter_id required"}, status=400)
        try:
            result = StronVendingService().clear_tamper(meter_id, customer_id)
            return Response({"result": result})
        except StronAPIError as exc:
            return Response({"detail": str(exc)}, status=400)
