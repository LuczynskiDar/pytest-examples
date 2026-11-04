import pytest
from src.shop.cart import Cart
from src.shop.customer import Customer
from src.shop.notifications import EmailNotifier
from src.shop.order import Order
from src.shop.payment import PaymentGateway
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
    return EmailNotifier("smtp.test.com", 25, "shop@example.com")


# Order
@pytest.fixture
def user_cart(correct_product: Product) -> Cart:
    cart = Cart()
    cart.add(correct_product, 2)
    return cart


@pytest.fixture
def correct_order(correct_customer: Customer, user_cart: Cart) -> Order:
    return Order(correct_customer, user_cart)


@pytest.fixture
def correct_payment_gateway() -> PaymentGateway:
    return PaymentGateway("api.example.com/payment/", "sh-test-secret-bearer", 3.0)


@pytest.fixture
def payment_success_response() -> dict[str, str]:
    return {"status": "approved", "transaction_id": "tx-12345"}


@pytest.fixture
def payment_fail_response() -> dict[str, str]:
    return {"status": "declined", "reason": "insufficient_funds"}
