from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="swagger-ui", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/meters/", include("apps.meters.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/tokens/", include("apps.tokens.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/stron/", include("apps.tokens.stron_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
