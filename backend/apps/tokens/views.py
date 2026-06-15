from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema

from apps.payments.serializers import ElectricityTokenSerializer
from apps.tokens.models import ElectricityToken


class TokenHistoryView(generics.ListAPIView):
    serializer_class = ElectricityTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            ElectricityToken.objects.filter(transaction__user=self.request.user)
            .select_related("transaction")
            .order_by("-generated_at")
        )

    @extend_schema(tags=["Tokens"], summary="List generated token history")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
