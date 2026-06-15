from django.db.models import Count, Sum
from rest_framework import permissions, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.audit.models import AuditLog
from apps.payments.models import Transaction
from apps.tokens.models import ElectricityToken
from apps.accounts.models import User
from apps.meters.models import Meter


class AdminDashboardView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=["Admin"], summary="Admin dashboard statistics")
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        stats = {
            "users": {
                "total": User.objects.count(),
                "verified": User.objects.filter(is_verified=True).count(),
            },
            "meters": {
                "total": Meter.objects.filter(is_active=True).count(),
            },
            "transactions": {
                "total": Transaction.objects.count(),
                "today": Transaction.objects.filter(created_at__date=today).count(),
                "completed": Transaction.objects.filter(status=Transaction.Status.COMPLETED).count(),
                "failed": Transaction.objects.filter(status=Transaction.Status.FAILED).count(),
                "pending": Transaction.objects.exclude(
                    status__in=[Transaction.Status.COMPLETED, Transaction.Status.FAILED]
                ).count(),
            },
            "revenue": {
                "total": str(
                    Transaction.objects.filter(status=Transaction.Status.COMPLETED).aggregate(
                        total=Sum("amount")
                    )["total"] or 0
                ),
                "today": str(
                    Transaction.objects.filter(
                        status=Transaction.Status.COMPLETED,
                        completed_at__date=today,
                    ).aggregate(total=Sum("amount"))["total"] or 0
                ),
                "week": str(
                    Transaction.objects.filter(
                        status=Transaction.Status.COMPLETED,
                        completed_at__date__gte=week_ago,
                    ).aggregate(total=Sum("amount"))["total"] or 0
                ),
            },
            "tokens": {
                "total_generated": ElectricityToken.objects.filter(
                    status__in=[ElectricityToken.Status.GENERATED, ElectricityToken.Status.DELIVERED]
                ).count(),
            },
            "recent_transactions": list(
                Transaction.objects.select_related("user", "meter")
                .order_by("-created_at")[:10]
                .values(
                    "reference", "amount", "status",
                    "user__phone_number", "meter__meter_number", "created_at",
                )
            ),
            "recent_audit_logs": list(
                AuditLog.objects.select_related("user")
                .order_by("-created_at")[:10]
                .values("action", "resource_type", "user__phone_number", "created_at")
            ),
        }
        return Response(stats)
