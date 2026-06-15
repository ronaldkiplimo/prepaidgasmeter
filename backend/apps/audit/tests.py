from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.audit.services import log_audit
from apps.audit.models import AuditLog

User = get_user_model()


class AuditLogTest(TestCase):
    def test_create_audit_log(self):
        user = User.objects.create_user(
            username="audituser",
            phone_number="254722222222",
            password="testpass123",
        )
        log = log_audit(
            user=user,
            action="TEST_ACTION",
            resource_type="Test",
            resource_id="123",
            details={"key": "value"},
        )
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(log.action, "TEST_ACTION")
