# Shop mini-project — description and requirements

A small online-shop domain model used to practise writing tests with pytest. There is no
database, no network and no I/O — everything is plain Python objects in memory.

## Overview

Four classes in `src/shop/`:

| Class | File | Responsibility |
|---|---|---|
| `Product` | `product.py` | An item with a name, price and stock level |
| `Cart` | `cart.py` | Products a customer wants to buy, with quantities |
| `Customer` | `customer.py` | A registered customer with a loyalty points balance |
| `Order` | `order.py` | A purchase made from a cart; has a lifecycle (new → paid → shipped) |

Dependencies between classes:

```
Product ◄── Cart ◄── Order ──► Customer
```

- `Cart` holds `Product` objects.
- `Order` is created from a `Customer` and a `Cart`, and changes the state of both the
  products (stock) and the customer (points) when paid.
- `Product` and `Customer` have no dependencies, so they are the easiest to start with.

## Technical requirements

- Python 3.12 or newer, managed with `uv`.
- Tests run with `uv run pytest` from the project root. Configuration is in
  `[tool.pytest.ini_options]` in `pyproject.toml` (`pythonpath = ["."]`, `testpaths = ["tests"]`).
- Imports use the project root: `from src.shop.product import Product`.
- Coverage is measured for `src` and printed with missing lines (`--cov=src`).
- The code language is English (names, messages, docstrings, comments).
- Every commit runs `ruff check --fix`, `ruff format` and `mypy` (strict) on `src` and `tests`,
  so tests must be fully type-annotated, e.g. `def test_add_stock() -> None:`.

## Product

A product available in the shop.

**Constructor:** `Product(name: str, price: float, stock: int = 0)`

| Rule | Behaviour |
|---|---|
| Negative price | `ValueError("Price cannot be negative")` |
| Negative stock | `ValueError("Stock cannot be negative")` |
| Price `0` or stock `0` | Allowed |

**Attributes:** `name`, `price`, `stock`.

| Method | Behaviour |
|---|---|
| `is_available()` | `True` if `stock > 0` |
| `add_stock(quantity)` | Increases stock. `quantity <= 0` → `ValueError("Quantity must be positive")` |
| `remove_stock(quantity)` | Decreases stock. `quantity <= 0` → `ValueError("Quantity must be positive")`; `quantity > stock` → `ValueError("Not enough stock")`. Removing exactly the whole stock is allowed |
| `apply_discount(percent)` | Returns the price after the discount, rounded to 2 decimals. Does **not** change `price`. `percent` outside `0..100` → `ValueError("Discount must be between 0 and 100")`. `0` and `100` are valid |

## Cart

A shopping cart holding products and their quantities. Items are stored in
`items: dict[str, tuple[Product, int]]`, keyed by product **name**.

| Method | Behaviour |
|---|---|
| `add(product, quantity=1)` | Adds the product. Adding the same product again increases its quantity. `quantity <= 0` → `ValueError("Quantity must be positive")`; `quantity > product.stock` → `ValueError("Not enough stock")` |
| `remove(product_name)` | Removes the product entirely (not one unit). Unknown name → `KeyError` |
| `total()` | Sum of `price * quantity`, rounded to 2 decimals. `0` for an empty cart |
| `count_items()` | Total number of units (sum of quantities), not the number of distinct products |
| `is_empty()` | `True` if the cart has no items |
| `clear()` | Removes all items |

## Customer

A registered shop customer with a loyalty points balance.

**Constructor:** `Customer(name: str, email: str)`

| Rule | Behaviour |
|---|---|
| Empty or whitespace-only name | `ValueError("Name cannot be empty")` |
| Name with surrounding spaces | Stored trimmed (`"  Anna "` → `"Anna"`) |
| Email not matching `EMAIL_PATTERN` | `ValueError("Invalid email address")` |
| New customer | Starts with `points = 0` |

Valid email: `local@domain.tld`, where the local part may contain letters, digits, `_`, `.`, `+`
and `-`.

| Method | Behaviour |
|---|---|
| `add_points(points)` | Increases the balance. `points <= 0` → `ValueError("Points must be positive")` |
| `redeem_points(points)` | Decreases the balance. `points <= 0` → `ValueError("Points must be positive")`; `points > balance` → `ValueError("Not enough points")`. Redeeming the whole balance is allowed |
| `get_status()` | `"standard"` for `< 500` points, `"silver"` for `500..999`, `"gold"` for `>= 1000` |

Boundary values worth testing: `499 / 500` and `999 / 1000`.

## Order

An order created from a customer's cart.

**Constructor:** `Order(customer: Customer, cart: Cart)`

- An empty cart → `ValueError("Cannot create an order from an empty cart")`.
- The order takes a **snapshot**: a copy of the cart's items and the cart's total as `subtotal`.
  Changing the cart afterwards does not affect the order.
- Initial `status` is `"new"`.

**Constants:** `STATUSES = ("new", "paid", "shipped", "cancelled")`, `SHIPPING_COST = 10.0`,
`FREE_SHIPPING_THRESHOLD = 100.0`.

| Method | Behaviour |
|---|---|
| `shipping_cost()` | `0.0` if `subtotal >= 100.0`, otherwise `10.0` |
| `total()` | `subtotal + shipping_cost()`, rounded to 2 decimals |
| `pay()` | Allowed only from `"new"`, otherwise `ValueError("Cannot pay for an order with status '<status>'")`. Removes the ordered quantities from each product's stock, adds `int(total())` points to the customer and sets status to `"paid"` |
| `ship()` | Allowed only from `"paid"`, otherwise `ValueError("Only paid orders can be shipped")`. Sets status to `"shipped"` |
| `cancel()` | Not allowed from `"shipped"` or `"cancelled"` → `ValueError("Cannot cancel an order with status '<status>'")`. Otherwise sets status to `"cancelled"` |

### Order status lifecycle

```
new ──pay()──► paid ──ship()──► shipped
 │              │
 └──cancel()────┴──cancel()──► cancelled
```

`shipped` and `cancelled` are final states.

## Known quirks (good test material)

These are the current behaviours of the code. They may be considered bugs or gaps — decide
whether a test should document them or whether the code should be fixed first.

1. **Cart stock check ignores what is already in the cart.** With `stock = 5`, `cart.add(p, 3)`
   twice succeeds and the cart holds 6 units.
2. **`Order.pay()` is not atomic.** If the second product has too little stock, the first product's
   stock has already been reduced when `ValueError` is raised, and the status stays `"new"`.
3. **`cancel()` after `pay()` does not restore anything.** Stock is not returned and the loyalty
   points are not taken back.
4. **Points are truncated, not rounded:** `int(total())`, so a total of `99.99` gives `99` points.
5. **`Cart.add` keeps the first `Product` object** for a given name. A different `Product` with
   the same name and a different price will not replace it.
6. **`Cart` is keyed by product name**, so two distinct products with the same name collide.
7. **Email is validated by a simple regex** and is not trimmed, unlike the name.

## Suggested test plan

Start from the classes with no dependencies and move up:

1. `Product` — validation, stock operations, `apply_discount`.
2. `Customer` — validation, points, status boundaries.
3. `Cart` — add/remove/total, using `Product` objects as test data.
4. `Order` — shipping cost threshold, status transitions, and the side effects of `pay()`.

Layout:

```
tests/
├── conftest.py        # shared fixtures: product, customer, cart
└── unit/
    ├── test_product.py
    ├── test_customer.py
    ├── test_cart.py
    └── test_order.py
```

pytest features that fit this project:

- `pytest.raises(..., match=...)` — every validation rule above.
- `@pytest.mark.parametrize` — status boundaries, shipping threshold, discount percentages.
- Fixtures — `Product`, `Customer` and `Cart` objects reused by `Order` tests.
- `pytest.approx` — price calculations with floats.
- Markers — the `unit` marker is already registered in `pyproject.toml`.
