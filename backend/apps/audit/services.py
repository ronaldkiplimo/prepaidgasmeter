from .models import AuditLog


def log_audit(
    action: str,
    resource_type: str,
    resource_id: str = "",
    user=None,
    details: dict | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
):
    """Create an immutable audit log entry."""
    return AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
