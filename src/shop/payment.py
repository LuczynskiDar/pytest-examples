import json
from urllib.error import URLError
from urllib.request import Request, urlopen


class PaymentError(Exception):
    """Raised when a payment cannot be completed."""


class PaymentGateway:
    """Client of an external payment service reached over HTTP."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def charge(self, amount: float, customer_email: str) -> str:
        """Charge the customer and return the transaction id.

        Raise ValueError for a non-positive amount and PaymentError if the service
        is unreachable or declines the payment.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        request = Request(
            f"{self.base_url}/charges",
            data=json.dumps({"amount": amount, "email": customer_email}).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except URLError as error:
            raise PaymentError("Payment gateway unavailable") from error

        if result.get("status") != "approved":
            raise PaymentError(f"Payment declined: {result.get('reason', 'unknown')}")
        return str(result["transaction_id"])
