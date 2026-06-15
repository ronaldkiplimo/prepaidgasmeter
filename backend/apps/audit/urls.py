from django.urls import path

from .dashboard import AdminDashboardView
from .views import AuditLogListView

urlpatterns = [
    path("logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
