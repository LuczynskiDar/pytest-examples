from src.shop.cart import Cart
from src.shop.customer import Customer


class Order:
    """An order created from a customer's cart."""

    STATUSES = ("new", "paid", "shipped", "cancelled")
    SHIPPING_COST = 10.0
    FREE_SHIPPING_THRESHOLD = 100.0

    def __init__(self, customer: Customer, cart: Cart):
        if cart.is_empty():
            raise ValueError("Cannot create an order from an empty cart")
        self.customer = customer
        self.items = dict(cart.items)
        self.subtotal = cart.total()
        self.status = "new"

    def shipping_cost(self) -> float:
        return 0.0 if self.subtotal >= self.FREE_SHIPPING_THRESHOLD else self.SHIPPING_COST

    def total(self) -> float:
        return round(self.subtotal + self.shipping_cost(), 2)

    def pay(self) -> None:
        if self.status != "new":
            raise ValueError(f"Cannot pay for an order with status '{self.status}'")
        for product, quantity in self.items.values():
            product.remove_stock(quantity)
        self.customer.add_points(int(self.total()))
        self.status = "paid"

    def ship(self) -> None:
        if self.status != "paid":
            raise ValueError("Only paid orders can be shipped")
        self.status = "shipped"

    def cancel(self) -> None:
        if self.status in ("shipped", "cancelled"):
            raise ValueError(f"Cannot cancel an order with status '{self.status}'")
        self.status = "cancelled"
