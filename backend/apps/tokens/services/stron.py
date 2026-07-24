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
        "vending_meter": "VendingMeter",
        "vending_direct": "VendingMeterDirectly",
        "clear_credit": "ClearCredit",
        "clear_tamper": "ClearTamper",
    }

    def __init__(self):
        self.base_url = settings.STRON_BASE_URL.rstrip("/")
        self.direct_base_url = settings.STRON_DIRECT_API_URL.rstrip("/")
        self.company_name = settings.STRON_COMPANY_NAME.strip()
        self.username = settings.STRON_USERNAME.strip()
        self.password = settings.STRON_PASSWORD.strip()
        self.vend_by_unit = settings.STRON_VEND_BY_UNIT
        self.use_direct_vending = settings.STRON_USE_DIRECT_VENDING

    def _credentials(self) -> dict:
        config_error = stron_config_error()
        if config_error:
            raise StronAPIError(config_error, retryable=False)
        return {
            "CompanyName": self.company_name,
            "UserName": self.username,
            "PassWord": self.password,
        }

    def _post(self, endpoint_key: str, payload: dict, timeout: int = 60, *, base_url: str | None = None):
        endpoint = self.ENDPOINTS[endpoint_key]
        url = f"{(base_url or self.base_url).rstrip('/')}/{endpoint}"
        # Log the request without sensitive credentials
        safe_payload = {k: v for k, v in payload.items() if k.lower() not in ("password", "password")}
        logger.info("Stron API %s -> %s payload=%s", endpoint_key, url, safe_payload)
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout,
            )
            response.raise_for_status()
            raw = response.json()
            logger.debug("Stron API %s response: %s", endpoint_key, raw)
            self._raise_for_api_error(raw, endpoint_key=endpoint_key)
            return raw
        except requests.RequestException as exc:
            logger.exception("Stron API request failed: %s (url=%s)", endpoint_key, url)
            raise StronAPIError(str(exc)) from exc

    def _raise_for_api_error(self, raw, *, endpoint_key: str = ""):
        # Dict with no ResultCode is a success payload (e.g. {"Token": "..."})
        if isinstance(raw, dict) and "ResultCode" not in raw:
            return

        if isinstance(raw, dict) and "ResultCode" in raw:
            result_code = raw.get("ResultCode")
            if str(result_code) == "0":
                return

            reason = (
                raw.get("Reason")
                or raw.get("ResultDesc")
                or raw.get("Message")
                or f"result code {result_code}"
            )
            logger.error("Stron API %s returned error response: %s", endpoint_key, raw)
            raise StronAPIError(
                f"Stron API error: {reason} (code {result_code})",
                response=raw,
                retryable=False,
            )

        # Handle non-dict responses (e.g. empty list []) from vending endpoints
        if isinstance(raw, list):
            if not raw:
                logger.error("Stron API %s returned empty list: %s", endpoint_key, raw)
                raise StronAPIError(
                    f"Stron API returned an empty list — vending failed. "
                    f"Check meter number, customer status, and Stron backend. "
                    f"endpoint={endpoint_key}",
                    response=raw,
                    retryable=False,
                )
            # Non-empty list: check each item for ResultCode errors
            for item in raw:
                if isinstance(item, dict) and "ResultCode" in item:
                    self._raise_for_api_error(item, endpoint_key=endpoint_key)
            # List with items — no ResultCode errors found, likely success data
            logger.debug("Stron API %s returned list with %d items (no errors)", endpoint_key, len(raw))
            return

        # Other unexpected response types (string, number, etc.)
        logger.error("Stron API %s returned unexpected type %s: %s", endpoint_key, type(raw).__name__, raw)
        raise StronAPIError(
            f"Stron API returned unexpected response type {type(raw).__name__}: {raw}",
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
            "Amount": self._format_amount_number(amount),
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
        """Backward-compatible alias for the documented VendingMeter endpoint."""
        return self.vending_meter(meter_id, amount, transaction_reference)

    def vending_direct(self, meter_id: str, amount: Decimal | float, transaction_reference: str = "") -> dict:
        payload = {
            **self._credentials(),
            "MeterId": meter_id,
            "Amount": self._format_amount(amount),  # String per v5.0.0 manual
        }
        logger.info("Stron VendingMeterDirectly meter=%s ref=%s", meter_id, transaction_reference)
        raw = self._post("vending_direct", payload, base_url=self.direct_base_url)
        return self._parse_vending_response(raw, amount)

    def vending_meter(self, meter_id: str, amount: Decimal | float, transaction_reference: str = "") -> dict:
        payload = {
            **self._credentials(),
            "MeterID": meter_id,
            "Amount": self._format_amount_number(amount),  # Number per v5.0.0 manual
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
        """Generate gas token after payment using the Stron manual's vending endpoints."""
        if self.use_direct_vending:
            return self.vending_direct(meter_number, amount, transaction_reference)
        return self.vending_meter(meter_number, amount, transaction_reference)

    def _parse_vending_response(self, raw, amount) -> dict:
        data = self._normalize(raw)
        token = self._extract(data, "Token", "TOKEN", "token")

        if not token:
            # Build a descriptive error message
            response_type = type(raw).__name__
            if isinstance(raw, (dict, list)):
                response_summary = json.dumps(raw, default=str, sort_keys=True)
            else:
                response_summary = str(raw)

            # Check if we can infer a reason from fields present in the response
            reason_hint = ""
            if isinstance(raw, dict):
                reason_hint = (
                    raw.get("Reason")
                    or raw.get("ResultDesc")
                    or raw.get("Message")
                    or ""
                )
            elif isinstance(raw, list) and raw and isinstance(raw[0], dict):
                reason_hint = (
                    raw[0].get("Reason")
                    or raw[0].get("ResultDesc")
                    or raw[0].get("Message")
                    or ""
                )

            if reason_hint:
                error_msg = (
                    f"Stron vending failed: {reason_hint}. "
                    f"No token returned. Endpoint response type={response_type}"
                )
            else:
                error_msg = (
                    f"Stron vending failed: did not return a token. "
                    f"Response type={response_type}, data={response_summary[:500]}. "
                    f"Check meter number, customer status, and Stron backend connectivity."
                )

            logger.error("Stron _parse_vending_response failure: %s", error_msg)
            raise StronAPIError(error_msg, response=raw)

        parsed = {
            "token": str(token),
            "token_units": self._extract(data, "Total_unit", "Unit", "Units", default=0),
            "token_amount": self._extract(data, "Total_paid", "Amount", "AMOUNT", default=amount),
            "receipt_number": self._extract(data, "ReceiptNumber", "Gen_time", default=""),
            "raw_response": raw if isinstance(raw, (dict, list)) else {"result": raw},
        }
        logger.info(
            "Stron token generated successfully: meter=****%s token=****%s units=%s",
            parsed.get("meter_number", "")[-4:] if parsed.get("meter_number") else "",
            str(parsed["token"])[-4:] if len(str(parsed["token"])) > 4 else str(parsed["token"]),
            parsed["token_units"],
        )
        return parsed

    @staticmethod
    def _format_amount(amount) -> str:
        """Format amount as string for APIs that expect string Amount (e.g. VendingMeterDirectly).

        Per v5.0.0 manual: VendingMeterDirectly Amount is a string ("30").
        """
        value = Decimal(str(amount))
        return format(value.normalize(), "f")

    @staticmethod
    def _format_amount_number(amount) -> int | float:
        """Format amount as a number for APIs that expect numeric Amount (e.g. VendingMeter).

        Per v5.0.0 manual: VendingMeter Amount is a number (100, not "100").
        """
        value = float(amount)
        if value == int(value):
            return int(value)
        return value
