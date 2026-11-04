import requests


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

        try:
            response = requests.post(
                f"{self.base_url}/charges",
                json={"amount": amount, "email": customer_email},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as error:
            raise PaymentError("Payment gateway unavailable") from error

        if result.get("status") != "approved":
            raise PaymentError(f"Payment declined: {result.get('reason', 'unknown')}")
        return str(result["transaction_id"])
