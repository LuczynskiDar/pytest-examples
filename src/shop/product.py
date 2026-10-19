class Product:
    """A product available in the shop."""

    def __init__(self, name: str, price: float, stock: int = 0):
        if price < 0:
            raise ValueError("Price cannot be negative")
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        self.name = name
        self.price = price
        self.stock = stock

    def is_available(self) -> bool:
        return self.stock > 0

    def add_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock += quantity

    def remove_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.stock:
            raise ValueError("Not enough stock")
        self.stock -= quantity

    def apply_discount(self, percent: float) -> float:
        """Return the price after discount without changing the product."""
        if not 0 <= percent <= 100:
            raise ValueError("Discount must be between 0 and 100")
        return round(self.price * (1 - percent / 100), 2)
