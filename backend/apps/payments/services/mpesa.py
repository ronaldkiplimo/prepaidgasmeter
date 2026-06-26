import base64
import hashlib
import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class MpesaService:
    """M-Pesa Daraja API integration for STK Push."""

    def __init__(self):
        self.base_url = settings.MPESA_BASE_URL
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL

    def _get_access_token(self) -> str:
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        credentials = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Basic {credentials}"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.RequestException as exc:
            detail = self._safe_response_detail(getattr(exc, "response", None))
            raise ValueError(f"M-Pesa token request failed{detail}.") from exc
        except (KeyError, ValueError) as exc:
            raise ValueError("M-Pesa token response did not include an access token.") from exc

    def _generate_password(self) -> tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        return password, timestamp

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: float,
        account_reference: str,
        transaction_desc: str,
    ) -> dict:
        """Initiate M-Pesa STK Push payment."""
        if (
            not self.consumer_key
            or not self.consumer_secret
            or not self.passkey
            or not self.callback_url
            or self.consumer_key.startswith("your-")
            or self.consumer_secret.startswith("your-")
            or self.passkey.startswith("your-")
            or "your-domain.com" in self.callback_url
        ):
            raise ValueError("M-Pesa credentials or callback URL are not configured. Update backend/.env before purchasing.")

        access_token = self._get_access_token()
        password, timestamp = self._generate_password()

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            detail = self._safe_response_detail(getattr(exc, "response", None))
            raise ValueError(f"M-Pesa STK push request failed{detail}.") from exc
        except ValueError as exc:
            raise ValueError("M-Pesa STK push response was not valid JSON.") from exc

    @staticmethod
    def _safe_response_detail(response) -> str:
        if response is None:
            return ""
        body = response.text.strip()[:300] if response.text else ""
        if body:
            return f" with HTTP {response.status_code}: {body}"
        return f" with HTTP {response.status_code}"

    @staticmethod
    def verify_callback(payload: dict) -> bool:
        """Verify M-Pesa callback payload structure and result code."""
        body = payload.get("Body", {})
        stk_callback = body.get("stkCallback", {})
        return bool(stk_callback.get("CheckoutRequestID"))

    @staticmethod
    def parse_callback(payload: dict) -> dict:
        """Parse M-Pesa STK callback into structured data."""
        stk_callback = payload.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        merchant_request_id = stk_callback.get("MerchantRequestID")

        result = {
            "checkout_request_id": checkout_request_id,
            "merchant_request_id": merchant_request_id,
            "result_code": result_code,
            "result_desc": stk_callback.get("ResultDesc", ""),
            "success": result_code == 0,
            "mpesa_receipt_number": "",
            "transaction_date": None,
            "phone_number": "",
            "amount": None,
        }

        if result["success"]:
            metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            for item in metadata:
                name = item.get("Name")
                value = item.get("Value")
                if name == "MpesaReceiptNumber":
                    result["mpesa_receipt_number"] = value
                elif name == "TransactionDate":
                    try:
                        dt_str = str(value)
                        result["transaction_date"] = datetime.strptime(
                            dt_str, "%Y%m%d%H%M%S"
                        )
                    except (ValueError, TypeError):
                        pass
                elif name == "PhoneNumber":
                    result["phone_number"] = str(value)
                elif name == "Amount":
                    result["amount"] = value

        return result

    @staticmethod
    def generate_idempotency_key(reference: str, amount: str) -> str:
        raw = f"{reference}:{amount}:{settings.SECRET_KEY[:16]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
