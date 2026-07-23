from apps.tokens.models import StronTransaction
from apps.tokens.services.stron import StronAPIError, StronVendingService


def log_stron_call(
    *,
    action: str,
    meter_number: str,
    request_payload: dict,
    response_payload=None,
    error_message: str = "",
    transaction=None,
    user_id=None,
    success: bool = True,
):
    return StronTransaction.objects.create(
        transaction=transaction,
        meter_number=meter_number,
        action=action,
        status=StronTransaction.Status.SUCCESS if success else StronTransaction.Status.FAILED,
        request_payload=request_payload,
        response_payload=response_payload or {},
        error_message=error_message,
        initiated_by_id=user_id,
    )


class StronServiceWithLogging(StronVendingService):
    """Stron service that logs every API call to stron_transactions."""

    def __init__(self, user=None, transaction=None):
        super().__init__()
        self.user = user
        self.transaction = transaction

    def _call(self, action, meter_number, fn, *args, **kwargs):
        payload = kwargs.pop("_payload", {})
        try:
            result = fn(*args, **kwargs)
            log_stron_call(
                action=action,
                meter_number=meter_number,
                request_payload=payload,
                response_payload=result if isinstance(result, (dict, list)) else {"result": result},
                transaction=self.transaction,
                user_id=str(self.user.id) if self.user else None,
            )
            return result
        except (StronAPIError, Exception) as exc:
            log_stron_call(
                action=action,
                meter_number=meter_number,
                request_payload=payload,
                response_payload=getattr(exc, "response", None) or {},
                error_message=str(exc),
                transaction=self.transaction,
                user_id=str(self.user.id) if self.user else None,
                success=False,
            )
            raise

    def query_meter_info(self, meter_id: str) -> dict:
        payload = {**self._credentials(), "MeterId": meter_id}
        return self._call(
            StronTransaction.Action.QUERY_METER_INFO,
            meter_id,
            super().query_meter_info,
            meter_id,
            _payload={"MeterId": meter_id},
        )

    def vending_preview(self, meter_id: str, amount):
        return self._call(
            StronTransaction.Action.VENDING_PREVIEW,
            meter_id,
            super().vending_preview,
            meter_id,
            amount,
            _payload={"MeterID": meter_id, "Amount": str(amount)},
        )

    def vending_purchase(self, meter_id: str, amount, transaction_reference: str = ""):
        return self._call(
            StronTransaction.Action.VENDING_METER,
            meter_id,
            super().vending_purchase,
            meter_id,
            amount,
            transaction_reference,
            _payload={"MeterID": meter_id, "Amount": str(amount)},
        )

    def vending_meter(self, meter_id: str, amount, transaction_reference: str = ""):
        return self._call(
            StronTransaction.Action.VENDING_METER,
            meter_id,
            super().vending_meter,
            meter_id,
            amount,
            transaction_reference,
            _payload={"MeterID": meter_id, "Amount": str(amount)},
        )

    def vending_direct(self, meter_id: str, amount, transaction_reference: str = ""):
        return self._call(
            StronTransaction.Action.VENDING_DIRECT,
            meter_id,
            super().vending_direct,
            meter_id,
            amount,
            transaction_reference,
            _payload={"MeterId": meter_id, "Amount": str(amount)},
        )
