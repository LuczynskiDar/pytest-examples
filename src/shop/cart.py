from src.shop.product import Product


class Cart:
    """A shopping cart holding products and their quantities."""

    def __init__(self) -> None:
        self.items: dict[str, tuple[Product, int]] = {}

    def add(self, product: Product, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > product.stock:
            raise ValueError("Not enough stock")
        _, current = self.items.get(product.name, (product, 0))
        self.items[product.name] = (product, current + quantity)

    def remove(self, product_name: str) -> None:
        if product_name not in self.items:
            raise KeyError(f"{product_name} is not in the cart")
        del self.items[product_name]

    def total(self) -> float:
        return round(sum(p.price * q for p, q in self.items.values()), 2)

    def count_items(self) -> int:
        return sum(q for _, q in self.items.values())

    def is_empty(self) -> bool:
        return not self.items

    def clear(self) -> None:
        self.items.clear()
