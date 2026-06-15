from django.test import TestCase
from apps.payments.services.mpesa import MpesaService


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
