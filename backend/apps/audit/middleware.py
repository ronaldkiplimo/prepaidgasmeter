import json
import logging

from .services import log_audit

logger = logging.getLogger(__name__)


class AuditMiddleware:
    """Log API requests for authenticated users."""

    SKIP_PATHS = {"/api/v1/payments/mpesa/callback/", "/api/docs/", "/api/schema/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.user.is_authenticated
            and request.path.startswith("/api/")
            and request.path not in self.SKIP_PATHS
            and request.method in ("POST", "PUT", "PATCH", "DELETE")
        ):
            try:
                log_audit(
                    user=request.user,
                    action=f"API_{request.method}",
                    resource_type="API",
                    resource_id=request.path,
                    details={"status_code": response.status_code},
                    ip_address=self._get_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                )
            except Exception:
                logger.exception("Failed to create audit log")

        return response

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
