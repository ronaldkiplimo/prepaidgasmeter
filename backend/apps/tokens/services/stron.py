import json
import logging
from decimal import Decimal

import requests
from django.conf import settings

from apps.core.config_check import stron_config_error

logger = logging.getLogger(__name__)


class StronAPIError(Exception):
    def __init__(self, message: str, response=None, retryable: bool = True):
        super().__init__(message)
        self.response = response
        self.retryable = retryable

    def __str__(self) -> str:
        base = super().__str__()
        details = self._response_details(self.response)
        if details:
            return f"{base} | response: {details}"
        return base

    @staticmethod
    def _response_details(response) -> str:
        if not response:
            return ""
        if isinstance(response, (dict, list)):
            try:
                return json.dumps(response, default=str, sort_keys=True)
            except TypeError:
                return str(response)
        return str(response)


class StronVendingService:
    """
    Stron Power Vending API v3.0.17
    Swagger: http://www.server-newv.stronpower.com/swagger/docs/v3.0.17
    """

    ENDPOINTS = {
        "query_customer_info": "QueryCustomerInfo",
        "query_meter_info": "QueryMeterInfo",
        "query_meter_credit": "QueryMeterCredit",
        "query_customer_credit": "QueryCustomerCredit",
        "vending_preview": "VendingMeterPreview",
        "vending_purchase": "VendingMeterPurchase",
        "vending_meter": "VendingMeter",
        "vending_direct": "VendingMeterDirectly",
        "clear_credit": "ClearCredit",
        "clear_tamper": "ClearTamper",
    }

    def __init__(self):
        self.base_url = settings.STRON_BASE_URL.rstrip("/")
        self.company_name = settings.STRON_COMPANY_NAME.strip()
        self.username = settings.STRON_USERNAME.strip()
        self.password = settings.STRON_PASSWORD.strip()
        self.vend_by_unit = settings.STRON_VEND_BY_UNIT

    def _credentials(self) -> dict:
        config_error = stron_config_error()
        if config_error:
            raise StronAPIError(config_error, retryable=False)
        return {
            "CompanyName": self.company_name,
            "UserName": self.username,
            "PassWord": self.password,
        }

    def _post(self, endpoint_key: str, payload: dict, timeout: int = 60):
        endpoint = self.ENDPOINTS[endpoint_key]
        url = f"{self.base_url}/{endpoint}"
        logger.info("Stron API %s -> %s", endpoint_key, url)
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout,
            )
            response.raise_for_status()
            raw = response.json()
            self._raise_for_api_error(raw)
            return raw
        except requests.RequestException as exc:
            logger.exception("Stron API request failed: %s", endpoint_key)
            raise StronAPIError(str(exc)) from exc

    def _raise_for_api_error(self, raw):
        if not isinstance(raw, dict) or "ResultCode" not in raw:
            return

        result_code = raw.get("ResultCode")
        if str(result_code) == "0":
            return

        reason = (
            raw.get("Reason")
            or raw.get("ResultDesc")
            or raw.get("Message")
            or f"result code {result_code}"
        )
        logger.error("Stron API returned error response: %s", raw)
        raise StronAPIError(
            f"Stron API error: {reason} (code {result_code})",
            response=raw,
            retryable=False,
        )

    def _unwrap_result(self, data):
        if isinstance(data, dict) and "Result" in data and "ResultCode" in data:
            return data.get("Result")
        return data

    def _normalize(self, data):
        data = self._unwrap_result(data)
        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict):
            return data
        return {}

    def _normalize_list(self, data):
        data = self._unwrap_result(data)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and data:
            return [data]
        return []

    def _extract(self, data: dict, *keys, default=None):
        for key in keys:
            if key in data and data[key] not in (None, ""):
                return data[key]
        return default

    def query_customer_info(self, customer_id: str) -> dict:
        payload = {**self._credentials(), "CustomerId": customer_id}
        raw = self._post("query_customer_info", payload, timeout=30)
        return self._normalize(raw)

    def query_meter_info(self, meter_id: str) -> dict:
        payload = {**self._credentials(), "MeterId": meter_id}
        raw = self._post("query_meter_info", payload, timeout=30)
        return self._normalize(raw)

    def query_meter_credit(self, meter_id: str) -> dict:
        payload = {**self._credentials(), "MeterId": meter_id}
        raw = self._post("query_meter_credit", payload, timeout=30)
        return self._normalize_list(raw)

    def query_customer_credit(self, customer_id: str) -> dict:
        payload = {**self._credentials(), "CustomerId": customer_id}
        raw = self._post("query_customer_credit", payload, timeout=30)
        return self._normalize_list(raw)

    def vending_preview(self, meter_id: str, amount: Decimal | float) -> dict:
        payload = {
            **self._credentials(),
            "MeterID": meter_id,
            "Amount": self._format_amount(amount),
            "is_vend_by_unit": str(self.vend_by_unit).lower(),
        }
        raw = self._post("vending_preview", payload, timeout=30)
        data = self._normalize(raw)
        return {
            "expected_units": self._extract(data, "Total_unit", "Unit", "Units", default=0),
            "expected_credit": self._extract(data, "NET_VALUE", "Amount", "Total_paid", default=amount),
            "vat": self._extract(data, "VAT", default=0),
            "price": self._extract(data, "Price", default=0),
            "rate": self._extract(data, "Rate", default=0),
            "raw_response": raw,
        }

    def vending_purchase(self, meter_id: str, amount: Decimal | float, transaction_reference: str = "") -> dict:
        """Final vending call after successful M-Pesa payment."""
        payload = {
            **self._credentials(),
            "MeterID": meter_id,
            "Amount": self._format_amount(amount),
            "is_vend_by_unit": str(self.vend_by_unit).lower(),
        }
        logger.info("Stron VendingMeterPurchase meter=%s ref=%s", meter_id, transaction_reference)
        raw = self._post("vending_purchase", payload)
        return self._parse_vending_response(raw, amount)

    def vending_meter(self, meter_id: str, amount: Decimal | float, transaction_reference: str = "") -> dict:
        payload = {
            **self._credentials(),
            "MeterID": meter_id,
            "Amount": self._format_amount(amount),
            "is_vend_by_unit": str(self.vend_by_unit).lower(),
        }
        logger.info("Stron VendingMeter meter=%s ref=%s", meter_id, transaction_reference)
        raw = self._post("vending_meter", payload)
        return self._parse_vending_response(raw, amount)

    def clear_credit(self, meter_id: str, customer_id: str = "") -> dict:
        payload = {**self._credentials(), "METER_ID": meter_id}
        if customer_id:
            payload["CustomerId"] = customer_id
        return self._post("clear_credit", payload, timeout=30)

    def clear_tamper(self, meter_id: str, customer_id: str = "") -> dict:
        payload = {**self._credentials(), "METER_ID": meter_id}
        if customer_id:
            payload["CustomerId"] = customer_id
        return self._post("clear_tamper", payload, timeout=30)

    def validate_meter(self, meter_number: str) -> dict:
        return self.query_meter_info(meter_number)

    def generate_token(
        self,
        meter_number: str,
        amount: float,
        transaction_reference: str,
        phone_number: str = "",
    ) -> dict:
        """Generate gas token after payment — uses VendingMeterPurchase."""
        return self.vending_purchase(meter_number, amount, transaction_reference)

    def _parse_vending_response(self, raw, amount) -> dict:
        data = self._normalize(raw)
        token = self._extract(data, "Token", "TOKEN", "token")
        if not token:
            raise StronAPIError(f"Stron did not return a token: {raw}", response=raw)
        return {
            "token": str(token),
            "token_units": self._extract(data, "Total_unit", "Unit", "Units", default=0),
            "token_amount": self._extract(data, "Total_paid", "Amount", "AMOUNT", default=amount),
            "receipt_number": self._extract(data, "ReceiptNumber", "Gen_time", default=""),
            "raw_response": raw if isinstance(raw, (dict, list)) else {"result": raw},
        }

    @staticmethod
    def _format_amount(amount) -> str:
        value = Decimal(str(amount))
        return format(value.normalize(), "f")
