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
