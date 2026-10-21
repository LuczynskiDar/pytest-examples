import pytest
from src.shop.product import Product


@pytest.fixture
def correct_product() -> Product:
    return Product("Battery", 10.25, 5)
