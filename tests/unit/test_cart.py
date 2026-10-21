import pytest
from src.shop.cart import Cart
from src.shop.product import Product


@pytest.mark.parametrize(
    ("test_qty", "error_msg"),
    [
        (-1, "Quantity must be positive"),
        (0, "Quantity must be positive"),
        (10, "Not enough stock"),
    ],
)
@pytest.mark.unit
def test_add_fail(
    correct_product: Product, correct_cart: Cart, test_qty: int, error_msg: str
) -> None:
    with pytest.raises(ValueError, match=error_msg):
        correct_cart.add(correct_product, test_qty)


@pytest.mark.parametrize(
    ("test_qty", "result"),
    [(2, 2)],
)
@pytest.mark.unit
def test_add(correct_product: Product, correct_cart: Cart, test_qty: int, result: int) -> None:
    correct_cart.add(correct_product, test_qty)
    product, qty = correct_cart.items.get(correct_product.name, (correct_product, 0))
    assert product.name == correct_product.name
    assert qty == result


@pytest.mark.parametrize(
    ("product_name", "error_msg"),
    [
        ("Bigos", "is not in the cart"),
    ],
)
@pytest.mark.unit
def test_remove_fail(product_name: str, correct_cart: Cart, error_msg: str) -> None:
    with pytest.raises(KeyError, match=f"{product_name} {error_msg}"):
        correct_cart.remove(product_name)


@pytest.mark.unit
def test_remove(correct_product: Product, correct_cart: Cart) -> None:
    assert len(correct_cart.items) == 0
    correct_cart.add(correct_product, 1)
    assert len(correct_cart.items) == 1
    correct_cart.remove(correct_product.name)
    assert len(correct_cart.items) == 0


@pytest.mark.unit
def test_count_items(correct_product: Product, correct_cart: Cart) -> None:
    assert correct_cart.count_items() == 0
    correct_cart.add(correct_product)
    assert correct_cart.count_items() == 1


@pytest.mark.unit
def test_is_empty(correct_product: Product, correct_cart: Cart) -> None:
    assert correct_cart.is_empty()
    correct_cart.add(correct_product)
    assert not correct_cart.is_empty()


@pytest.mark.unit
def test_clear(correct_product: Product, correct_cart: Cart) -> None:
    assert correct_cart.is_empty()
    correct_cart.add(correct_product, 1)
    assert not correct_cart.is_empty()
    correct_cart.clear()
    assert correct_cart.is_empty()


@pytest.mark.unit
def test_total(correct_product: Product, correct_cart: Cart) -> None:
    assert correct_cart.is_empty()
    correct_cart.add(correct_product, 3)
    total = correct_cart.total()
    assert total == 30.75
