import logging
import uuid

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class StronVendingService:
    """Stron Vending API integration for gas meter token generation."""

    def __init__(self):
        self.base_url = settings.STRON_API_URL.rstrip("/")
        self.api_key = settings.STRON_API_KEY
        self.merchant_id = settings.STRON_MERCHANT_ID

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Merchant-ID": self.merchant_id,
        }

    def validate_meter(self, meter_number: str) -> dict:
        """Validate meter number with Stron API."""
        url = f"{self.base_url}/meters/validate"
        response = requests.post(
            url,
            json={"meter_number": meter_number, "merchant_id": self.merchant_id},
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def generate_token(
        self,
        meter_number: str,
        amount: float,
        transaction_reference: str,
        phone_number: str,
    ) -> dict:
        """Generate prepaid gas meter token via Stron Vending API."""
        url = f"{self.base_url}/tokens/vend"
        payload = {
            "merchant_id": self.merchant_id,
            "meter_number": meter_number,
            "amount": amount,
            "transaction_reference": transaction_reference,
            "phone_number": phone_number,
            "idempotency_key": str(uuid.uuid5(uuid.NAMESPACE_DNS, transaction_reference)),
        }

        logger.info("Requesting token from Stron for meter %s, ref %s", meter_number, transaction_reference)

        response = requests.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "token": data.get("token", data.get("vending_token", "")),
            "token_units": data.get("units", data.get("token_units", 0)),
            "token_amount": data.get("amount", amount),
            "receipt_number": data.get("receipt_number", ""),
            "raw_response": data,
        }

    def query_token_status(self, transaction_reference: str) -> dict:
        """Query token generation status."""
        url = f"{self.base_url}/tokens/status/{transaction_reference}"
        response = requests.get(url, headers=self._headers(), timeout=30)
        response.raise_for_status()
        return response.json()
