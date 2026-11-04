import pytest
from src.shop.cart import Cart
from src.shop.customer import Customer
from src.shop.order import Order
from src.shop.product import Product


@pytest.mark.unit
def test_empty_cart(correct_customer: Customer) -> None:
    cart = Cart()
    with pytest.raises(ValueError, match="Cannot create an order from an empty cart"):
        Order(correct_customer, cart)


@pytest.mark.unit
def test_order_parameters(
    correct_order: Order, correct_customer: Customer, user_cart: Cart
) -> None:
    assert correct_order.customer == correct_customer
    assert correct_order.items == dict(user_cart.items)
    assert correct_order.subtotal == user_cart.total()
    assert correct_order.status == "new"


@pytest.mark.parametrize(
    ("product_name", "product_price", "product_stock", "cart_qty", "ship_cost"),
    [("Tablet X", 100.0, 10, 2, 0.0), ("Battery", 10.25, 5, 2, 10.0)],
)
@pytest.mark.unit
def test_shipping_cost(
    correct_customer: Customer,
    product_name: str,
    product_price: float,
    product_stock: int,
    cart_qty: int,
    ship_cost: float,
) -> None:
    product = Product(product_name, product_price, product_stock)
    cart = Cart()
    cart.add(product, cart_qty)
    order = Order(correct_customer, cart)
    assert order.shipping_cost() == ship_cost


@pytest.mark.parametrize(
    ("product_name", "product_price", "product_stock", "cart_qty", "ship_cost"),
    [("Tablet X", 100.0, 10, 2, 0.0), ("Battery", 10.25, 5, 2, 10.0)],
)
@pytest.mark.unit
def test_total(
    correct_customer: Customer,
    product_name: str,
    product_price: float,
    product_stock: int,
    cart_qty: int,
    ship_cost: float,
) -> None:
    product = Product(product_name, product_price, product_stock)
    cart = Cart()
    cart.add(product, cart_qty)
    order = Order(correct_customer, cart)
    assert order.total() == round(cart.total() + ship_cost, 2)


@pytest.mark.unit
def test_pay(correct_cart: Cart, correct_customer: Customer, correct_product: Product) -> None:

    to_remove = 2

    correct_cart.add(correct_product, to_remove)
    order = Order(correct_customer, correct_cart)

    current_stock = correct_product.stock

    cart_total = correct_cart.total()
    ship_cost = order.shipping_cost()
    total_cost = round(cart_total + ship_cost, 2)

    current_points = correct_customer.points
    customer_points = int(total_cost)

    order.pay()
    assert order.status == "paid"
    assert order.customer.points == current_points + customer_points
    product_qty = order.items[correct_product.name][0].stock
    assert product_qty == current_stock - to_remove


@pytest.mark.unit
def test_pay_fail(correct_order: Order) -> None:
    correct_order.status = "cancelled"
    with pytest.raises(
        ValueError, match=f"Cannot pay for an order with status '{correct_order.status}'"
    ):
        correct_order.pay()


@pytest.mark.unit
def test_ship(correct_order: Order) -> None:
    correct_order.status = "paid"
    correct_order.ship()
    assert correct_order.status == "shipped"


@pytest.mark.unit
def test_ship_fail(correct_order: Order) -> None:
    correct_order.status = "cancelled"
    with pytest.raises(ValueError, match="Only paid orders can be shipped"):
        correct_order.ship()


@pytest.mark.unit
def test_cancel(correct_order: Order) -> None:
    correct_order.status = "paid"
    correct_order.cancel()
    assert correct_order.status == "cancelled"


@pytest.mark.parametrize(
    "test_status",
    [
        ("shipped"),
        ("cancelled"),
    ],
)
@pytest.mark.unit
def test_cancel_fail(correct_order: Order, test_status: str) -> None:
    correct_order.status = test_status
    with pytest.raises(
        ValueError, match=f"Cannot cancel an order with status '{correct_order.status}'"
    ):
        correct_order.cancel()
