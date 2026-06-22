from django.urls import path

from .views import AnalyticsDashboardView, SalesReportView

urlpatterns = [
    path("analytics/", AnalyticsDashboardView.as_view(), name="analytics-dashboard"),
    path("sales/", SalesReportView.as_view(), name="sales-report"),
]
