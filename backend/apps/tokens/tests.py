from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from apps.tokens.services.stron import StronAPIError, StronVendingService


@override_settings(
    STRON_BASE_URL="http://www.server-newv.stronpower.com/api",
    STRON_COMPANY_NAME="Stron-Good",
    STRON_USERNAME="Admin01",
    STRON_PASSWORD="123456",
    STRON_VEND_BY_UNIT=False,
    STRON_DIRECT_API_URL="http://www.server-api.stronpower.com/api",
    STRON_USE_DIRECT_VENDING=False,
)
class StronVendingServiceTest(SimpleTestCase):
    @patch("apps.tokens.services.stron.requests.post")
    def test_generate_token_uses_documented_vending_meter_payload(self, post):
        post.return_value = self._response([{"Token": "1234-5678-9012", "Total_unit": "12.5", "Total_paid": "100"}])

        result = StronVendingService().generate_token(
            meter_number="58100711868",
            amount=100,
            transaction_reference="TXN123",
            phone_number="254712345678",
        )

        post.assert_called_once_with(
            "http://www.server-newv.stronpower.com/api/VendingMeter",
            json={
                "CompanyName": "Stron-Good",
                "UserName": "Admin01",
                "PassWord": "123456",
                "MeterID": "58100711868",
                "Amount": 100,  # Number per v5.0.0 manual (not string)
                "is_vend_by_unit": "false",
            },
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        self.assertEqual(result["token"], "1234-5678-9012")
        self.assertEqual(result["token_units"], "12.5")
        self.assertEqual(result["token_amount"], "100")

    @override_settings(STRON_USE_DIRECT_VENDING=True)
    @patch("apps.tokens.services.stron.requests.post")
    def test_generate_token_can_use_direct_vending_payload(self, post):
        post.return_value = self._response([{"Token": "1234-5678-9012", "Total_unit": "12.5", "Total_paid": "100"}])

        result = StronVendingService().generate_token(
            meter_number="58100711868",
            amount=100,
            transaction_reference="TXN123",
            phone_number="254712345678",
        )

        post.assert_called_once_with(
            "http://www.server-api.stronpower.com/api/VendingMeterDirectly",
            json={
                "CompanyName": "Stron-Good",
                "UserName": "Admin01",
                "PassWord": "123456",
                "MeterId": "58100711868",
                "Amount": "100",
            },
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        self.assertEqual(result["token"], "1234-5678-9012")

    @patch("apps.tokens.services.stron.requests.post")
    def test_vending_meter_uses_vending_meter_endpoint(self, post):
        post.return_value = self._response([{"Meter_id": "58100711868", "Token": "9999-8888"}])

        result = StronVendingService().vending_meter(
            meter_id="58100711868",
            amount=30,
            transaction_reference="TXN123",
        )

        post.assert_called_once_with(
            "http://www.server-newv.stronpower.com/api/VendingMeter",
            json={
                "CompanyName": "Stron-Good",
                "UserName": "Admin01",
                "PassWord": "123456",
                "MeterID": "58100711868",
                "Amount": 30,  # Number per v5.0.0 manual (not string)
                "is_vend_by_unit": "false",
            },
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        self.assertEqual(result["token"], "9999-8888")

    @patch("apps.tokens.services.stron.requests.post")
    def test_wrapped_vending_response_unwraps_result(self, post):
        post.return_value = self._response({
            "ResultCode": 0,
            "Result": {"Token": "5555-6666", "Total_unit": "4.5", "Total_paid": "50"},
            "Reason": "",
        })

        result = StronVendingService().vending_meter("58100711868", 50, "TXN123")

        self.assertEqual(result["token"], "5555-6666")
        self.assertEqual(result["token_units"], "4.5")
        self.assertEqual(result["token_amount"], "50")

    @patch("apps.tokens.services.stron.requests.post")
    def test_api_error_result_code_raises_non_retryable_error(self, post):
        payload = {"ResultCode": 1, "Result": {"Message": "Invalid meter number"}, "Reason": "API Error"}
        post.return_value = self._response(payload)

        with self.assertRaises(StronAPIError) as exc:
            StronVendingService().vending_meter("58100711868", 50, "TXN123")

        self.assertFalse(exc.exception.retryable)
        self.assertEqual(exc.exception.response, payload)
        self.assertIn("API Error", str(exc.exception))
        self.assertIn("Invalid meter number", str(exc.exception))

    def test_missing_credentials_raise_clear_error(self):
        with override_settings(STRON_COMPANY_NAME="your-company-name"):
            with self.assertRaisesMessage(StronAPIError, "Stron Power API is not configured"):
                StronVendingService().generate_token(
                    meter_number="58100711868",
                    amount=100,
                    transaction_reference="TXN123",
                    phone_number="254712345678",
                )

    @staticmethod
    def _response(data):
        response = Mock()
        response.json.return_value = data
        response.raise_for_status.return_value = None
        return response
