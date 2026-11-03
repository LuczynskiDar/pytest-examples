import pytest
from src.shop.cart import Cart
from src.shop.customer import Customer
from src.shop.notifications import EmailNotifier
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


# EmailNotifier("smtp.example.com")                  # port domyślny 25
# EmailNotifier("smtp.example.com", 587)             # port 587 (STARTTLS)
# EmailNotifier("localhost", 1025)                   # lokalny serwer testowy
# "smtp.gmail.com": nazwa domenowa
# "127.0.0.1": adres IP
# "localhost": lokalny kompute


@pytest.fixture
def correct_email_notifier() -> EmailNotifier:
    return EmailNotifier("test@example.com", 25, "shop@example.com")
