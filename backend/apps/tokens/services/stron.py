import logging
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class StronVendingService:
    """Stron Vending API integration for gas meter token generation."""

    def __init__(self):
        self.base_url = settings.STRON_API_URL.rstrip("/")
        self.direct_base_url = settings.STRON_DIRECT_API_URL.rstrip("/")
        self.company_name = settings.STRON_COMPANY_NAME.strip()
        self.username = settings.STRON_USERNAME.strip()
        self.password = settings.STRON_PASSWORD.strip()
        self.vend_by_unit = settings.STRON_VEND_BY_UNIT
        self.use_direct_vending = settings.STRON_USE_DIRECT_VENDING

    def _credentials(self) -> dict:
        if (
            not self.company_name
            or not self.username
            or not self.password
            or self.company_name.startswith("your-")
            or self.username.startswith("your-")
            or self.password.startswith("your-")
        ):
            raise ValueError("Stron credentials are not configured. Update backend/.env before vending tokens.")

        return {
            "CompanyName": self.company_name,
            "UserName": self.username,
            "PassWord": self.password,
        }

    def _post(self, endpoint: str, payload: dict, *, direct: bool = False, timeout: int = 60) -> dict:
        base_url = self.direct_base_url if direct else self.base_url
        url = f"{base_url}/{endpoint.lstrip('/')}"
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

    def validate_meter(self, meter_number: str) -> dict:
        """Query meter information with Stron's QueryMeterInfo endpoint."""
        payload = {
            **self._credentials(),
            "MeterId": meter_number,
        }
        return self._post("QueryMeterInfo", payload, timeout=30)

    def generate_token(
        self,
        meter_number: str,
        amount: float,
        transaction_reference: str,
        phone_number: str,
    ) -> dict:
        """Generate prepaid gas meter token via Stron Vending API."""
        direct = self.use_direct_vending
        payload = {
            **self._credentials(),
            "Amount": self._format_amount(amount),
        }

        if direct:
            payload["MeterID"] = meter_number
            endpoint = "VendingMeterDirectly"
        else:
            payload["MeterID"] = meter_number
            payload["is_vend_by_unit"] = str(self.vend_by_unit).lower()
            endpoint = "VendingMeter"

        logger.info("Requesting token from Stron for meter %s, ref %s", meter_number, transaction_reference)

        raw_data = self._post(endpoint, payload, direct=direct)
        data = self._normalize_response(raw_data)
        token = self._extract_first(data, "token", "Token", "TOKEN", "VendingToken", "vending_token", "CreditToken")
        if not token:
            raise ValueError(f"Stron response did not include a token: {raw_data}")

        return {
            "token": token,
            "token_units": self._extract_first(
                data,
                "Total_unit",
                "Unit",
                "Units",
                "units",
                "token_units",
                default=0,
            ),
            "token_amount": self._extract_first(
                data,
                "AMOUNT",
                "Amount",
                "amount",
                "Total_paid",
                "token_amount",
                default=amount,
            ),
            "receipt_number": self._extract_first(
                data,
                "ReceiptNumber",
                "receipt_number",
                "ReceiptNo",
                "SerialNo",
                "OrderNo",
                default="",
            ),
            "raw_response": raw_data,
        }

    def query_meter_credit(self, meter_number: str) -> dict:
        """Query meter credit records with Stron's QueryMeterCredit endpoint."""
        payload = {
            **self._credentials(),
            "MeterId": meter_number,
        }
        return self._post("QueryMeterCredit", payload, timeout=30)

    def query_token_status(self, transaction_reference: str) -> dict:
        """Compatibility method; Stron's manual does not expose reference-based token status."""
        raise NotImplementedError("Stron API manual does not define a transaction-reference token status endpoint.")

    def _extract_first(self, data: dict, *keys: str, default=None):
        for key in keys:
            if key in data and data[key] not in (None, ""):
                return data[key]

        for value in data.values():
            if isinstance(value, dict):
                nested = self._extract_first(value, *keys, default=None)
                if nested not in (None, ""):
                    return nested

        return default

    def _normalize_response(self, data):
        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict):
            return data
        return {}

    def _format_amount(self, amount) -> str:
        value = Decimal(str(amount))
        return format(value.normalize(), "f")
