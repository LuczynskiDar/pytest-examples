from unittest.mock import patch

import pytest
import requests
from src.shop.customer import Customer
from src.shop.payment import PaymentError, PaymentGateway


@pytest.mark.unit
def test_paymet_gateway(correct_payment_gateway: PaymentGateway) -> None:
    assert not correct_payment_gateway.base_url.endswith("/")


@pytest.mark.parametrize(("test_amount"), [(100.0)])
@pytest.mark.unit
def test_charge(
    correct_payment_gateway: PaymentGateway,
    payment_success_response: dict[str, str],
    correct_customer: Customer,
    test_amount: float,
) -> None:

    with patch("src.shop.payment.requests.post") as mock_post:
        mock_post.return_value.json.return_value = payment_success_response
        trsnsaction_id = correct_payment_gateway.charge(test_amount, correct_customer.email)

    assert trsnsaction_id == payment_success_response["transaction_id"]


@pytest.mark.parametrize(("test_amount"), [(0.0), (-1.0)])
@pytest.mark.unit
def test_charge_fail_due_to_low_amount(
    correct_payment_gateway: PaymentGateway, correct_customer: Customer, test_amount: float
) -> None:
    with pytest.raises(ValueError, match="Amount must be positive"):
        correct_payment_gateway.charge(test_amount, correct_customer.email)


@pytest.mark.parametrize(("test_status_code"), [(401), (503)])
@pytest.mark.unit
def test_charge_fail_due_to_status_code(
    correct_payment_gateway: PaymentGateway, correct_customer: Customer, test_status_code: int
) -> None:
    test_amount = 100.0
    with patch("src.shop.payment.requests.post") as mock_post:
        mock_post.return_value.status_code = test_status_code
        mock_post.return_value.raise_for_status.side_effect = requests.HTTPError(
            str(test_status_code)
        )
        with pytest.raises(PaymentError, match="Payment gateway unavailable"):
            correct_payment_gateway.charge(test_amount, correct_customer.email)


@pytest.mark.unit
def test_charge_fail_due_to_payment_declined(
    correct_payment_gateway: PaymentGateway,
    payment_fail_response: dict[str, str],
    correct_customer: Customer,
) -> None:
    test_amount = 100.0
    with patch("src.shop.payment.requests.post") as mock_post:
        mock_post.return_value.json.return_value = payment_fail_response
        with pytest.raises(PaymentError, match="Payment declined: "):
            correct_payment_gateway.charge(test_amount, correct_customer.email)
