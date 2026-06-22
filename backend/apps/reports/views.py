from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import permissions, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.core.permissions import IsAdminOrDistributor, IsAdminOrLandlordOrDistributor
from apps.meters.models import Meter
from apps.payments.models import Transaction
from apps.tokens.models import GasToken
from django.contrib.auth import get_user_model

User = get_user_model()


class AnalyticsDashboardView(views.APIView):
    permission_classes = [IsAdminOrDistributor]

    @extend_schema(tags=["Analytics"], summary="Platform analytics dashboard")
    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        completed = Transaction.objects.filter(status=Transaction.Status.COMPLETED)
        return Response({
            "total_revenue": str(completed.aggregate(t=Sum("amount"))["t"] or 0),
            "today_revenue": str(completed.filter(completed_at__date=today).aggregate(t=Sum("amount"))["t"] or 0),
            "week_revenue": str(completed.filter(completed_at__date__gte=week_ago).aggregate(t=Sum("amount"))["t"] or 0),
            "month_revenue": str(completed.filter(completed_at__date__gte=month_ago).aggregate(t=Sum("amount"))["t"] or 0),
            "total_customers": User.objects.filter(role="customer").count(),
            "active_meters": Meter.objects.filter(is_active=True, status="active").count(),
            "offline_meters": Meter.objects.filter(status="offline").count(),
            "tampered_meters": Meter.objects.filter(tamper_status=True).count(),
            "gas_sold_units": str(GasToken.objects.aggregate(t=Sum("token_units"))["t"] or 0),
            "failed_transactions": Transaction.objects.filter(status=Transaction.Status.FAILED).count(),
            "pending_transactions": Transaction.objects.exclude(
                status__in=[Transaction.Status.COMPLETED, Transaction.Status.FAILED]
            ).count(),
        })


class SalesReportView(views.APIView):
    permission_classes = [IsAdminOrLandlordOrDistributor]

    @extend_schema(tags=["Reports"], summary="Daily/monthly sales report")
    def get(self, request):
        period = request.query_params.get("period", "daily")
        days = 30 if period == "monthly" else 7
        since = timezone.now().date() - timedelta(days=days)

        txns = (
            Transaction.objects.filter(status=Transaction.Status.COMPLETED, completed_at__date__gte=since)
            .values("completed_at__date")
            .annotate(count=Count("id"), revenue=Sum("amount"), units=Sum("gas_token__token_units"))
            .order_by("completed_at__date")
        )
        return Response({"period": period, "data": list(txns)})
