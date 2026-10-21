import pytest
from src.shop.customer import Customer
from tests.test_helpers import CustomerData


@pytest.mark.parametrize(
    ("test_customer", "error_msg"),
    [
        (("", "test@example.com"), "Name cannot be empty"),
        ((" ", "test@example.com"), "Name cannot be empty"),
    ],
)
@pytest.mark.unit
def test_customer_name_fail(test_customer: CustomerData, error_msg: str) -> None:
    with pytest.raises(ValueError, match=error_msg):
        Customer(*test_customer)


@pytest.mark.parametrize(
    ("test_customer", "error_msg"),
    [
        (("Test", "test.example.com"), "Invalid email address"),
        (("Test", "test@example"), "Invalid email address"),
    ],
)
@pytest.mark.unit
def test_customer_email_fail(test_customer: CustomerData, error_msg: str) -> None:
    with pytest.raises(ValueError, match=error_msg):
        Customer(*test_customer)


@pytest.mark.parametrize(
    ("test_points", "error_msg"),
    [
        (-1, "Points must be positive"),
        (0, "Points must be positive"),
    ],
)
@pytest.mark.unit
def test_add_points_fail(correct_customer: Customer, test_points: int, error_msg: str) -> None:
    with pytest.raises(ValueError, match=error_msg):
        correct_customer.add_points(test_points)


@pytest.mark.parametrize(
    ("test_points", "result"),
    [
        (100, 100),
    ],
)
@pytest.mark.unit
def test_add_points(correct_customer: Customer, test_points: int, result: int) -> None:
    assert correct_customer.points == 0
    correct_customer.add_points(test_points)
    assert correct_customer.points == result


@pytest.mark.parametrize(
    ("test_points", "error_msg"),
    [
        (-1, "Points must be positive"),
        (0, "Points must be positive"),
        (1, "Not enough points"),
    ],
)
@pytest.mark.unit
def test_redeem_points_fail(correct_customer: Customer, test_points: int, error_msg: str) -> None:
    with pytest.raises(ValueError, match=error_msg):
        correct_customer.redeem_points(test_points)


@pytest.mark.parametrize(
    ("test_points", "result"),
    [
        (100, 100),
    ],
)
@pytest.mark.unit
def test_redeem_points(correct_customer: Customer, test_points: int, result: int) -> None:
    assert correct_customer.points == 0
    correct_customer.add_points(test_points)
    assert correct_customer.points == result
    correct_customer.redeem_points(test_points)
    assert correct_customer.points == 0


@pytest.mark.parametrize(
    ("test_points", "result"),
    [
        (1000, "gold"),
        (1001, "gold"),
        (500, "silver"),
        (501, "silver"),
        (100, "standard"),
    ],
)
@pytest.mark.unit
def test_get_status(correct_customer: Customer, test_points: int, result: str) -> None:
    assert correct_customer.points == 0
    correct_customer.add_points(test_points)
    assert correct_customer.points == test_points
    assert correct_customer.get_status() == result
