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

## File reading — `src/files/readers.py`

Plain functions, no dependencies. All accept `Path` or `str`. Sample files are in `data/`, but
tests should mostly create their own with the `tmp_path` fixture.

| Function | Behaviour |
|---|---|
| `read_text(path)` | Whole file content as a string (UTF-8). Missing file → `FileNotFoundError` |
| `read_lines(path)` | Lines stripped of surrounding whitespace; empty lines and lines starting with `#` are skipped |
| `read_json(path)` | Parsed JSON (any type). Invalid JSON → `ValueError("Invalid JSON in <path>: <reason>")`. Missing file → `FileNotFoundError` |
| `read_csv(path, delimiter=",", required_columns=())` | List of dicts keyed by the header; every value is a **string**. File with no header → `ValueError("CSV file is empty: <path>")`; missing required columns → `ValueError("Missing columns: a, b")` |

Things worth testing: empty file, file with only comments, header-only CSV (returns `[]`),
custom delimiter (`;`), non-ASCII characters (UTF-8), a malformed JSON, a missing file.

## Importing products — `src/shop/importer.py`

`ProductImporter` builds `Product` objects from files, using the readers above.

| Method | Behaviour |
|---|---|
| `load_from_csv(path)` | CSV with required columns `name`, `price` and optional `stock` (empty or missing → `0`). Missing required column → `ValueError("Missing columns: ...")` |
| `load_from_json(path)` | JSON list of objects with the same keys (values may be strings or numbers). Not a list → `ValueError("JSON file must contain a list of products")` |

Both methods report an invalid entry as `ValueError("Invalid product in row <n>: <reason>")`,
where `n` counts data rows from 1. Causes: a non-numeric price or stock, a missing key, a negative
price or stock (the `Product` validation message is included in `<reason>`).

## Payment — `src/shop/payment.py`

`PaymentGateway(base_url, api_key, timeout=5.0)` talks to an external service over HTTP using
`urllib.request.urlopen`. **Tests must never make a real request — mock `urlopen`.**

`charge(amount, customer_email) -> str` sends `POST <base_url>/charges` with a JSON body and a
`Bearer` token, and returns the transaction id.

| Situation | Result |
|---|---|
| `amount <= 0` | `ValueError("Amount must be positive")`, no request is made |
| Response `{"status": "approved", "transaction_id": ...}` | Returns the id as a string |
| Response with another status | `PaymentError("Payment declined: <reason>")`, reason defaults to `unknown` |
| `URLError` from `urlopen` | `PaymentError("Payment gateway unavailable")` |

Things to verify with a mock: the `Request` object passed to `urlopen` (URL, method, headers,
body) and the `timeout` argument.

## Notifications — `src/shop/notifications.py`

`EmailNotifier(host, port=25, sender="shop@example.com")` sends mail through `smtplib.SMTP`.
**Tests must mock `smtplib.SMTP`.**

| Method | Behaviour |
|---|---|
| `send(recipient, subject, body)` | Builds an `EmailMessage` (From, To, Subject, body) and sends it with `send_message` inside a `with smtplib.SMTP(host, port)` block |
| `send_order_confirmation(order)` | Sends to the customer's e-mail, subject `"Order confirmation"`, body with the customer's name and `order.total()` formatted to 2 decimals |

## Checkout — `src/shop/order_service.py`

`OrderService(gateway, notifier)` combines the pieces. It receives its collaborators through the
constructor, so they are easy to replace with `Mock` / `MagicMock`.

`checkout(order) -> str`:

1. Order status other than `"new"` → `ValueError("Cannot check out an order with status '<status>'")`;
   the customer is **not** charged.
2. Charges `order.total()` for `order.customer.email` through the gateway.
3. Calls `order.pay()` (stock is reduced, points are added).
4. Sends the confirmation e-mail. An `smtplib.SMTPException` is **logged** as a warning
   (`"Could not send confirmation to <email>"`) and does not fail the checkout.
5. Returns the transaction id.

| Scenario | Expected |
|---|---|
| Gateway raises `PaymentError` | The error propagates; order stays `"new"`; notifier is not called |
| Notifier raises `SMTPException` | Checkout still returns the id; order is `"paid"`; a warning is logged (`caplog`) |
| Happy path | `gateway.charge` called once with `(order.total(), email)`; `notifier.send_order_confirmation` called once with the order |

## Mocking cheat sheet

| Goal | Tool |
|---|---|
| Replace a collaborator passed via the constructor | `Mock()` / `MagicMock()`; `Mock(spec=PaymentGateway)` rejects unknown attributes |
| Make a call return a value or raise | `mock.charge.return_value = "tx-1"`, `mock.charge.side_effect = PaymentError("...")` |
| Replace a name used inside a module | `patch("src.shop.payment.urlopen")` — patch where the name is **used**, not where it is defined |
| Mock a context manager (`with urlopen(...) as r`) | Configure `mock.return_value.__enter__.return_value` |
| Check calls | `assert_called_once_with(...)`, `assert_not_called()`, `call_args`, `call_count` |
| Check logging | `caplog` fixture (`caplog.at_level(logging.WARNING)`, `caplog.messages`) |
| Create files for reader tests | `tmp_path`, then `(tmp_path / "x.csv").write_text(...)` |

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
5. `readers` — txt, json and csv with files created in `tmp_path`.
6. `ProductImporter` — real files from `tmp_path`; later, the same with `read_csv` mocked.
7. `PaymentGateway` and `EmailNotifier` — mock `urlopen` and `smtplib.SMTP`.
8. `OrderService` — mock the gateway and the notifier; check calls, errors and logging.

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
