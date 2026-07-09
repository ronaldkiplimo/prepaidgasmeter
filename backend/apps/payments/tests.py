from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.meters.models import Meter
from apps.payments.models import Payment, Transaction
from apps.payments.services.mpesa import MpesaService

User = get_user_model()


class MpesaServiceTest(TestCase):
    def test_verify_callback_valid(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_123",
                    "ResultCode": 0,
                }
            }
        }
        self.assertTrue(MpesaService.verify_callback(payload))

    def test_verify_callback_invalid(self):
        self.assertFalse(MpesaService.verify_callback({}))

    def test_parse_callback_success(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_123",
                    "MerchantRequestID": "mr_123",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "MpesaReceiptNumber", "Value": "QAB123"},
                            {"Name": "Amount", "Value": 500},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    },
                }
            }
        }
        result = MpesaService.parse_callback(payload)
        self.assertTrue(result["success"])
        self.assertEqual(result["mpesa_receipt_number"], "QAB123")
        self.assertEqual(result["amount"], 500)

    def test_parse_callback_treats_string_zero_as_success(self):
        payload = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_123",
                    "ResultCode": "0",
                    "ResultDesc": "Success",
                }
            }
        }
        result = MpesaService.parse_callback(payload)
        self.assertTrue(result["success"])


class MpesaCallbackTokenGenerationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            phone_number="254700000010",
            password="testpass123",
        )
        self.meter = Meter.objects.create(user=self.user, meter_number="11111111")
        self.transaction = Transaction.objects.create(
            reference="PGKCALLBACK",
            user=self.user,
            meter=self.meter,
            amount="100.00",
            total_amount="100.00",
            phone_number=self.user.phone_number,
            status=Transaction.Status.PAYMENT_INITIATED,
        )
        self.payment = Payment.objects.create(
            transaction=self.transaction,
            amount="100.00",
            phone_number=self.user.phone_number,
            status=Payment.Status.PENDING,
            checkout_request_id="ws_CO_123",
            merchant_request_id="mr_123",
        )

    @patch("apps.payments.views.generate_token_task.delay")
    def test_successful_callback_queues_token_generation_after_commit(self, delay):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                "/api/v1/payments/mpesa/callback/",
                data=self._success_callback(),
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        delay.assert_called_once_with(str(self.transaction.id))

        self.transaction.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.transaction.status, Transaction.Status.PAYMENT_CONFIRMED)
        self.assertEqual(self.payment.status, Payment.Status.SUCCESS)

    @patch("apps.payments.views.generate_token_task.delay")
    def test_duplicate_success_callback_requeues_when_token_is_missing(self, delay):
        self.payment.status = Payment.Status.SUCCESS
        self.payment.save(update_fields=["status", "updated_at"])
        self.transaction.status = Transaction.Status.PAYMENT_CONFIRMED
        self.transaction.save(update_fields=["status", "updated_at"])

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                "/api/v1/payments/mpesa/callback/",
                data=self._success_callback(),
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        delay.assert_called_once_with(str(self.transaction.id))

    def _success_callback(self):
        return {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": self.payment.checkout_request_id,
                    "MerchantRequestID": self.payment.merchant_request_id,
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "MpesaReceiptNumber", "Value": "QAB123"},
                            {"Name": "Amount", "Value": 100},
                            {"Name": "PhoneNumber", "Value": 254700000010},
                        ]
                    },
                }
            }
        }


class PaymentMeterAccessTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            phone_number="254700000010",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            phone_number="254700000011",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            username="admin",
            phone_number="254700000012",
            password="testpass123",
            role=User.Role.ADMIN,
        )
        self.meter = Meter.objects.create(user=self.user, meter_number="11111111")
        self.other_meter = Meter.objects.create(user=self.other_user, meter_number="22222222")
        self.transaction = Transaction.objects.create(
            reference="PGKOWNED",
            user=self.user,
            meter=self.meter,
            amount="100.00",
            phone_number=self.user.phone_number,
        )
        self.other_transaction = Transaction.objects.create(
            reference="PGKOTHER",
            user=self.other_user,
            meter=self.other_meter,
            amount="100.00",
            phone_number=self.other_user.phone_number,
        )
        self.client.force_authenticate(user=self.user)

    def test_user_transaction_list_only_includes_own_transactions(self):
        response = self.client.get("/api/v1/payments/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        references = {txn["reference"] for txn in data}
        self.assertEqual(references, {"PGKOWNED"})

    def test_user_cannot_view_other_users_transaction_detail(self):
        response = self.client.get("/api/v1/payments/transactions/PGKOTHER/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_view_any_transaction_detail(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/payments/transactions/PGKOTHER/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_lookup_other_users_meter(self):
        response = self.client.get("/api/v1/payments/meters/22222222/lookup/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
