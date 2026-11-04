from unittest.mock import patch

from src.shop.customer import Customer
from src.shop.payment import PaymentGateway


def test_paymet_gateway(correct_payment_gateway: PaymentGateway) -> None:
    assert not correct_payment_gateway.base_url.endswith("/")


def test_charge(
    correct_payment_gateway: PaymentGateway,
    payment_success_response: dict[str, str],
    correct_customer: Customer,
) -> None:
    amount = 100.0

    with patch("src.shop.payment.requests.post") as mock_post:
        mock_post.return_value.json.return_value = payment_success_response
        trsnsaction_id = correct_payment_gateway.charge(amount, correct_customer.email)

    assert trsnsaction_id == payment_success_response["transaction_id"]
