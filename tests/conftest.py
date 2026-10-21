import pytest
from src.shop.cart import Cart
from src.shop.customer import Customer
from src.shop.product import Product


@pytest.fixture
def correct_product() -> Product:
    return Product("Battery", 10.25, 5)


@pytest.fixture
def correct_customer() -> Customer:
    return Customer("Test", "test@example.com")


@pytest.fixture
def correct_cart() -> Cart:
    return Cart()
