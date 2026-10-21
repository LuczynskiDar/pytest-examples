import pytest
from src.shop.product import Product
from tests.test_helpers import ProductData


@pytest.mark.parametrize("invalid_product_data", [("Battery", -10.25, 5)])
@pytest.mark.unit
def test_product_negative_price(invalid_product_data: ProductData) -> None:
    with pytest.raises(ValueError, match="Price cannot be negative"):
        Product(*invalid_product_data)


@pytest.mark.parametrize("invalid_product_data", [("Battery", 10.25, -5)])
@pytest.mark.unit
def test_product_negative_stock(invalid_product_data: ProductData) -> None:
    with pytest.raises(ValueError, match="Stock cannot be negative") as err:
        Product(*invalid_product_data)
    assert err.type is ValueError
    assert str(err.value) == "Stock cannot be negative"


@pytest.mark.parametrize(
    ("product", "expected_result"),
    [(Product("Battery", 10.25, 5), True), (Product("Battery", 10.25, 0), False)],
)
@pytest.mark.unit
def test_is_available(product: Product, expected_result: bool) -> None:
    assert product.is_available() == expected_result


@pytest.mark.parametrize(
    "test_qty",
    [
        (-1),
        (0),
    ],
)
@pytest.mark.unit
def test_add_stock_failed(correct_product: Product, test_qty: int) -> None:
    with pytest.raises(ValueError, match="Quantity must be positive"):
        correct_product.add_stock(test_qty)


@pytest.mark.parametrize(
    ("test_qty", "result"),
    [
        (5, 10),
    ],
)
@pytest.mark.unit
def test_add_stock(correct_product: Product, test_qty: int, result: int) -> None:
    correct_product.add_stock(test_qty)
    assert correct_product.stock == result


@pytest.mark.parametrize(
    ("test_qty", "error_msg"),
    [
        (-1, "Quantity must be positive"),
        (0, "Quantity must be positive"),
        (6, "Not enough stock"),
    ],
)
@pytest.mark.unit
def test_remove_stock_failed(correct_product: Product, test_qty: int, error_msg: str) -> None:
    with pytest.raises(ValueError, match=error_msg):
        correct_product.remove_stock(test_qty)


@pytest.mark.parametrize(
    ("test_qty", "result"),
    [
        (4, 1),
    ],
)
@pytest.mark.unit
def test_remove_stock(correct_product: Product, test_qty: int, result: int) -> None:
    correct_product.remove_stock(test_qty)
    assert correct_product.stock == result


@pytest.mark.parametrize(
    ("fail_percent", "error_msg"),
    [
        (-0.1, "Discount must be between 0 and 100"),
        (101.0, "Discount must be between 0 and 100"),
    ],
)
@pytest.mark.unit
def test_apply_discount_failed(
    correct_product: Product, fail_percent: float, error_msg: str
) -> None:
    with pytest.raises(ValueError, match=error_msg):
        correct_product.apply_discount(fail_percent)


@pytest.mark.parametrize(
    ("test_discount", "result"),
    [
        (99, 0.1),
        (1, 10.15),
    ],
)
@pytest.mark.unit
def test_apply_discount(correct_product: Product, test_discount: float, result: float) -> None:
    discount = correct_product.apply_discount(test_discount)
    assert discount == result
