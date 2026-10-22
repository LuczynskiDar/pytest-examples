# Teoria testowania

## Unit testy vs Integration testy

### Unit testy

Testują **jedną, izolowaną jednostkę kodu** — funkcję, metodę, klasę.

Kluczowa zasada: **izolacja**. Jeśli funkcja zależy od bazy danych, zewnętrznego API,
systemu plików — w unit teście to **mockujesz** (zastępujesz fałszywym obiektem).
Interesuje Cię tylko logika tej jednej funkcji.

**Cechy:**
- Bardzo szybkie (milisekundy)
- Dużo ich piszesz
- Łatwe do debugowania — kiedy padną, wiesz *dokładnie* co nie działa
- Nie mówią Ci czy system jako całość działa

### Integration testy

Testują **współpracę kilku komponentów** — np. czy Twój kod poprawnie zapisuje do bazy,
czy dwa moduły razem dają właściwy wynik.

Tu **nie mockujesz** (albo mockujesz tylko granice zewnętrzne, np. zewnętrzne API).
Używasz prawdziwej bazy, prawdziwego filesystemu.

**Cechy:**
- Wolniejsze
- Mniej ich piszesz
- Trudniejsze do debugowania — gdy padną, przyczyna może być gdziekolwiek
- Dają pewność że system *naprawdę* działa

---

## Piramida testów

Klasyczny model:

```
        /\
       /  \   E2E (end-to-end) — najmniej
      /----\
     /      \ Integration — średnio
    /--------\
   /          \ Unit — najwięcej
  /____________\
```

Więcej unit testów, mniej integration, jeszcze mniej E2E.
Powód: koszt pisania i utrzymania rośnie w górę piramidy.

---

## Kluczowe pytania przy każdym kawałku kodu

1. **Co tu jest logiką biznesową?** → unit test
2. **Co tu jest integracją z zewnętrznym systemem?** → integration test

---

## Cechy dobrego unit testu — zasada FIRST

| Litera | Znaczenie | Co to oznacza w praktyce |
|--------|-----------|--------------------------|
| **F** | Fast | Działa w milisekundach, nie sekundach |
| **I** | Isolated | Nie zależy od innych testów ani zewnętrznych systemów |
| **R** | Repeatable | Zawsze daje ten sam wynik, niezależnie od środowiska |
| **S** | Self-validating | Sam mówi czy przeszedł czy nie (asercje, nie logi) |
| **T** | Timely | Pisany razem z kodem (lub przed — patrz TDD) |

---

## Struktura unit testu — wzorzec AAA

Każdy test składa się z trzech faz:

```
Arrange  →  przygotuj dane wejściowe i zależności
Act      →  wywołaj testowaną funkcję
Assert   →  sprawdź czy wynik jest zgodny z oczekiwaniem
```

Przykład (pseudokod):

```python
def test_oblicz_vat():
    # Arrange
    cena_netto = 100

    # Act
    wynik = oblicz_vat(cena_netto, stawka=0.23)

    # Assert
    assert wynik == 123
```

---

## Co mockować, czego nie?

**Mockujesz** wszystko co jest *poza* testowaną funkcją:
- baza danych
- zewnętrzne API
- system plików
- czas (`datetime.now()`)
- losowość (`random`)

**Nie mockujesz** logiki biznesowej — to właśnie testujesz.

---

## Jeden test = jedna rzecz

Każdy test powinien sprawdzać **dokładnie jedną sytuację**.

Jeśli test sprawdza pięć rzeczy naraz — kiedy padnie, nie wiesz która z nich zawiodła.
Lepiej mieć pięć małych testów niż jeden duży.

---

## Narzędzia — pytest

Standardowy framework do testów w Pythonie. Alternatywa dla wbudowanego `unittest`,
ale znacznie wygodniejsza w użyciu.

### Dlaczego pytest, nie unittest?

| Cecha | pytest | unittest |
|-------|--------|----------|
| Składnia asercji | `assert x == y` | `self.assertEqual(x, y)` |
| Fixtures | elastyczne, reużywalne | ograniczone (setUp/tearDown) |
| Pluginy | bogaty ekosystem | brak |
| Czytelność błędów | bardzo dobra | przeciętna |

### Jak działa?

pytest automatycznie wykrywa pliki testowe i funkcje testowe po nazwie:
- plik: `test_*.py` lub `*_test.py`
- funkcja: `def test_*`

```python
# test_przyklad.py

def test_dodawanie():
    assert 2 + 2 == 4
```

Uruchomienie: `pytest` (wykrywa wszystko automatycznie)

### Fixtures

Fixture to mechanizm do przygotowania i sprzątania zasobów potrzebnych w teście.
Zastępuje `setUp` / `tearDown` z unittest, ale jest bardziej elastyczny.

```python
import pytest

@pytest.fixture
def przykladowy_uzytkownik():
    return {"id": 1, "imie": "Jan"}

def test_imie_uzytkownika(przykladowy_uzytkownik):
    assert przykladowy_uzytkownik["imie"] == "Jan"
```

Fixture można reużywać w wielu testach — nie duplikujesz kodu przygotowania danych.

#### Fixture z adnotacjami typów (mypy strict)

```python
@pytest.fixture
def product() -> Product:
    return Product("Laptop", 100.0, stock=5)


def test_remove_stock(product: Product) -> None:
    product.remove_stock(2)
    assert product.stock == 3
```

- Pytest wstrzykuje fixture **po nazwie argumentu** testu.
- Domyślnie (`scope="function"`) każdy test dostaje **nową instancję**, więc testy nie
  wpływają na siebie nawzajem.
- Fixture współdzieloną między plikami umieść w `tests/conftest.py` — pytest znajduje ją
  automatycznie, bez importu.

#### Fixture zależna od innej fixture

Fixture może przyjmować inne fixtures jako argumenty. To dobry sposób na budowanie
obiektów złożonych z prostszych (np. `Order` z `Customer` i `Cart`):

```python
@pytest.fixture
def cart(product: Product) -> Cart:
    cart = Cart()
    cart.add(product, 2)
    return cart


@pytest.fixture
def order(customer: Customer, cart: Cart) -> Order:
    return Order(customer, cart)
```

#### Sprzątanie przez `yield`

Kod po `yield` wykona się po teście, nawet gdy test padł:

```python
@pytest.fixture
def temp_file(tmp_path: Path) -> Iterator[Path]:
    file = tmp_path / "data.txt"
    file.write_text("data")
    yield file
    file.unlink(missing_ok=True)   # sprzątanie
```

### `conftest.py` — co w nim umieszczać

`conftest.py` to plik, który pytest **ładuje sam**, bez importu, przed testami z danego katalogu
i jego podkatalogów. Nazwa musi być dokładnie `conftest.py` (literówka, np. `contest.py`, sprawia,
że plik jest ignorowany, a fixtures niewidoczne).

#### Co powinno tam być

| Element | Przykład |
|---|---|
| **Fixtures współdzielone** między wieloma plikami testów | `product`, `customer`, `cart` |
| **Hooki pytesta** | `pytest_configure`, `pytest_collection_modifyitems` |
| **Rejestracja pluginów** | `pytest_plugins = ["..."]` |
| **Fixtures z `autouse=True`** dla całego katalogu | czyszczenie stanu, ustawienie zmiennej środowiskowej |

```python
# tests/conftest.py
import pytest

from src.shop.product import Product


@pytest.fixture
def product() -> Product:
    return Product("Battery", 10.25, 5)
```

Test używa fixture po nazwie argumentu, bez żadnego importu:

```python
def test_is_available(product: Product) -> None:
    assert product.is_available()
```

#### Czego tam nie umieszczać

- **Zwykłych funkcji pomocniczych, stałych i aliasów typów** (np. `ProductData = tuple[str, float, int]`),
  które testy importują ręcznie. Do tego służy osobny moduł, np. `tests/helpers.py`.
- **Testów** (`test_*`). Pytest ich z `conftest.py` nie zbiera.
- **Fixtures używanych tylko w jednym pliku.** Trzymaj je w tym pliku, blisko testów, które z nich
  korzystają.
- **Logiki biznesowej** albo dużych zestawów danych. Plik ma pozostać krótki i czytelny.

#### Dlaczego nie importować z `conftest.py`

Wzorzec `from tests.conftest import ProductData` jest niezalecany:

- Pytest wczytuje `conftest.py` pod własną nazwą modułu, a ręczny import ładuje go **drugi raz**
  jako `tests.conftest`. Zależnie od `--import-mode` i obecności `__init__.py` możesz dostać dwa
  osobne moduły albo błąd importu.
- Z nazwy `conftest` nie wynika, że definiuje typy lub stałe używane w testach.

Poprawnie: fixtures w `conftest.py` (wstrzykiwane przez pytest), a współdzielone typy i funkcje
w osobnym module:

```python
# tests/helpers.py
ProductData = tuple[str, float, int]
```

```python
# tests/unit/test_product.py
from tests.helpers import ProductData
```

Alias używany w jednym pliku zostaw w tym pliku i przenieś do `helpers.py` dopiero wtedy,
gdy będzie potrzebny w drugim.

#### Wiele plików `conftest.py` i zasięg

Pytest szuka `conftest.py` w każdym katalogu na drodze do testu. Fixture jest widoczna dla testów
w tym katalogu i **wszystkich podkatalogach**, a plik głębiej może ją **nadpisać** fixture o tej samej
nazwie.

```
tests/
├── conftest.py            # fixtures dla całego projektu: product, customer, cart
├── helpers.py             # wspólne typy i funkcje (importowane ręcznie)
├── unit/
│   ├── conftest.py        # opcjonalnie: fixtures tylko dla unit testów
│   └── test_product.py
└── integration/
    ├── conftest.py        # np. fixtures z bazą danych, tylko dla integration
    └── test_order_flow.py
```

Zasada: fixture umieszczaj **na najniższym poziomie, który wystarcza**. Używana w jednym pliku
zostaje w tym pliku, w jednym katalogu trafia do jego `conftest.py`, a w całym projekcie do
`tests/conftest.py`.

#### Konwencje

- **Nazewnictwo fixtures:** nazwa opisuje to, co fixture zwraca (`product`, `empty_cart`), bez
  prefiksu `test_`. W pliku z testami pytest wziąłby `test_product` za test.
- **Adnotacje typów:** fixture zwraca typ obiektu (`-> Product`); przy `yield` używaj
  `Iterator[T]` lub `Generator[T, None, None]`.
- **Zakres (`scope`):** domyślny `function` daje świeży obiekt na test. Szerszy zakres
  (`module`, `session`) tylko dla drogich zasobów, które nie są mutowane.
- **Jedna odpowiedzialność:** fixture buduje jeden obiekt. Złożone obiekty składaj z mniejszych
  fixtures (patrz wyżej, „Fixture zależna od innej fixture").

### Hooki pytesta

**Hook** to funkcja o ściśle określonej nazwie, którą **pytest sam wywołuje** w konkretnym
momencie swojego działania (start, zbieranie testów, wykonanie testu, raport). Nie wywołujesz jej
w testach ani nie wstrzykujesz — wystarczy zdefiniować funkcję o właściwej nazwie w `conftest.py`
(albo we wtyczce), a pytest ją znajdzie i uruchomi.

Nazwy hooków zaczynają się od `pytest_`. Literówka w nazwie z tym prefiksem nie przechodzi po cichu:
pytest kończy się błędem `PluginValidationError: unknown hook 'pytest_colection_modifyitems'`.

#### Hook a fixture

| | Fixture | Hook |
|---|---|---|
| Kto wywołuje | pytest, gdy test poprosi o nią przez argument | pytest, automatycznie w ustalonym momencie |
| Do czego | przygotować dane i zasoby dla testu | zmienić zachowanie samego pytesta |
| Nazwa | dowolna | narzucona przez pytest |
| Dostęp do testów | tylko do tego, który jej użył | do całej sesji, wszystkich zebranych testów i wyników |

Zasada: **najpierw fixtures**, hooki dopiero gdy fixture nie wystarcza. Hook zmienia zachowanie
pytesta globalnie, więc nadużywanie utrudnia zrozumienie, dlaczego test działa tak, a nie inaczej.

#### Najważniejsze hooki w kolejności działania

| Faza | Hook | Do czego |
|---|---|---|
| Start | `pytest_addoption` | dodać własną opcję linii poleceń (`--run-slow`) |
| Start | `pytest_configure` | zarejestrować markery, ustawić konfigurację |
| Zbieranie testów | `pytest_collection_modifyitems` | zmienić listę testów: pominąć, dodać marker, posortować |
| Wykonanie | `pytest_runtest_setup` / `_call` / `_teardown` | zareagować przed, w trakcie i po teście |
| Wynik | `pytest_runtest_makereport` | przechwycić wynik testu (np. zapisać logi przy porażce) |
| Raport | `pytest_report_header`, `pytest_terminal_summary` | dopisać własne linie do raportu |
| Koniec | `pytest_sessionfinish`, `pytest_unconfigure` | posprzątać po całej sesji |

#### Przykład 1: automatyczny marker na podstawie katalogu

Zamiast `@pytest.mark.unit` nad każdym testem, hook oznacza wszystkie testy z `tests/unit/`:

```python
# tests/conftest.py
import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if "unit" in item.path.parts:
            item.add_marker(pytest.mark.unit)
```

Wtedy `pytest -m unit` wybiera wszystkie testy z tego katalogu. `item.path` to `pathlib.Path`
pliku testu, a `items` można modyfikować (dodawać markery, usuwać elementy, zmieniać kolejność).

#### Przykład 2: własna opcja `--run-slow`

Wolne testy są domyślnie pomijane, a uruchamiasz je świadomie. Trzy hooki współpracują:

```python
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "slow: tests that take a long time")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-slow"):
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
```

- `pytest_addoption` dodaje flagę, `pytest_configure` rejestruje marker (odpowiednik sekcji
  `markers` w `pyproject.toml`), a `pytest_collection_modifyitems` pomija oznaczone testy.
- Użycie w teście: `@pytest.mark.slow`. Domyślnie test jest pomijany (`pytest -rs` pokaże powód),
  a `pytest --run-slow` uruchamia wszystko.

#### Przykład 3: dopisek do nagłówka raportu

```python
def pytest_report_header(config: pytest.Config) -> str:
    return "project: pytest-examples (shop)"
```

Zwrócony tekst pojawia się w nagłówku, obok wersji Pythona i pytesta.

#### Przykład 4: reakcja na wynik testu (hook wrapper)

`pytest_runtest_makereport` jako **wrapper** otacza domyślne zachowanie: `yield` zwraca gotowy raport,
a po nim możesz zareagować. Przydatne np. do zapisania logów lub zrzutu ekranu przy porażce:

```python
from collections.abc import Generator
from typing import Any


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, Any, Any]:
    report = yield
    if report.when == "call" and report.failed:
        print(f"\nFAILED: {item.nodeid}")
    return report
```

`report.when` ma wartość `setup`, `call` lub `teardown`. Wrapper musi **zwrócić** raport.
To zaawansowany wzorzec — na początku nauki zwykle niepotrzebny.

#### Zasięg i zasady

- **Adnotacje typów:** w mypy strict hooki wymagają adnotacji jak każda funkcja
  (`pytest.Config`, `pytest.Item`, `pytest.Parser`, `-> None`).
- **Zasięg:** `conftest.py` działa na testy ze swojego katalogu i podkatalogów. Hooki globalne, jak
  `pytest_addoption`, umieszczaj w głównym `tests/conftest.py` (lub wtyczce) — opcje linii poleceń
  są czytane, zanim pytest zbierze testy z podkatalogów.
- **Kilka implementacji tego samego hooka** (w różnych plikach `conftest.py`) uruchamia się wszystkie,
  nie tylko ostatnia.
- **Podstawa wtyczek:** `pytest-cov` i `pytest-asyncio` to w dużej mierze zestawy hooków.
  Sprawdzisz, jakie hooki wywołuje pytest, przez `pytest --trace-config`, a pełną listę z opisem
  znajdziesz w dokumentacji „Hook reference".

### Named Tuple w testach

Named tuple to krotka której pola mają nazwy. W testach używana do czytelnego
opisywania przypadków testowych w `parametrize`.

**Sposób 1 — `collections.namedtuple`** (starszy, bez typów)

```python
from collections import namedtuple

HealthCase = namedtuple("HealthCase", ["environment", "is_dev", "expected"])
```

**Sposób 2 — `typing.NamedTuple`** (nowocześniejszy, z typami)

```python
from typing import NamedTuple

class HealthCase(NamedTuple):
    environment: str
    is_dev: bool
    expected: dict
```

**Sposób 3 — `typing.NamedTuple` z wartościami domyślnymi**

Gdy niektóre pola są opcjonalne — podajesz wartość domyślną po typie:

```python
class HealthCase(NamedTuple):
    environment: str
    is_dev: bool
    expected_status: str = "ok"       # domyślnie "ok"
    expected_debug: bool | None = None  # domyślnie None
```

Dzięki temu możesz tworzyć instancje bez podawania wszystkich pól:

```python
HealthCase(environment="production", is_dev=False)
# expected_status = "ok", expected_debug = None — automatycznie
```

**Użycie w `parametrize`:**

```python
@pytest.mark.parametrize("case", [
    HealthCase(environment="development", is_dev=True),
    HealthCase(environment="production", is_dev=False),
])
async def test_health(case):
    # dostęp po nazwie zamiast po indeksie
    mock_settings.is_dev = case.is_dev
    assert response["status"] == case.expected_status
```

**Co zyskujesz vs zwykła krotka:**

| Krotka pozycyjna | Named tuple |
|-----------------|-------------|
| `(True, False, "ok")` | `is_dev=True, is_prod=False, expected="ok"` |
| `case[0]` | `case.is_dev` |
| Łatwo przestawić kolejność przez pomyłkę | Jawne przypisanie po nazwie |

### `pytest.mark.parametrize`

Pozwala uruchomić ten sam test z różnymi zestawami danych wejściowych.
Zamiast pisać trzy osobne funkcje — piszesz jedną z listą przypadków:

```python
@pytest.mark.parametrize("a,b,wynik", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_dodawanie(a, b, wynik):
    assert dodaj(a, b) == wynik
```

Kiedy `parametrize` ma sens — gdy przypadki mają **identyczną strukturę**,
różnią się tylko wartościami. Gdy asercje różnią się strukturą — lepsze są oddzielne funkcje.

#### Nazwy argumentów jako krotka i adnotacje typów

Z mypy strict każdy parametr testu musi mieć typ. Nazwy argumentów można podać jako krotkę
(zamiast jednego stringa z przecinkami):

```python
@pytest.mark.parametrize(
    ("percent", "expected"),
    [
        (0, 100.0),
        (25, 75.0),
        (100, 0.0),
    ],
)
def test_apply_discount(percent: float, expected: float) -> None:
    assert Product("Laptop", 100.0).apply_discount(percent) == expected
```

#### Czytelne nazwy przypadków — `pytest.param` i `id`

Domyślnie przypadki mają nazwy typu `test_apply_discount[25-75.0]`. Własne `id` poprawia raport:

```python
@pytest.mark.parametrize(
    ("percent", "expected"),
    [
        pytest.param(0, 100.0, id="no-discount"),
        pytest.param(25, 75.0, id="quarter"),
        pytest.param(100, 0.0, id="free"),
    ],
)
def test_apply_discount(percent: float, expected: float) -> None:
    ...
```

Pojedynczy przypadek można też oznaczyć markerem, np. `pytest.param(..., marks=pytest.mark.xfail)`.

#### `parametrize` razem z `pytest.raises`

Jeden test dla wielu niepoprawnych danych wejściowych, każda z innym komunikatem:

```python
@pytest.mark.parametrize(
    ("price", "stock", "message"),
    [
        pytest.param(-1, 0, "Price cannot be negative", id="negative-price"),
        pytest.param(10, -1, "Stock cannot be negative", id="negative-stock"),
    ],
)
def test_product_invalid_arguments(price: float, stock: int, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Product("Laptop", price, stock)
```

#### Wartości graniczne

`parametrize` świetnie nadaje się do testowania granic (testy z obu stron progu):

```python
@pytest.mark.parametrize(
    ("points", "status"),
    [(0, "standard"), (499, "standard"), (500, "silver"), (999, "silver"), (1000, "gold")],
)
def test_customer_status(points: int, status: str) -> None:
    customer = Customer("Anna", "anna@example.com")
    customer.points = points
    assert customer.get_status() == status
```

### Pułapka — `parametrize` + `patch` jako dekorator

Dekoratory nakładają się od dołu do góry. Każdy `@patch` dodaje argument do funkcji
— też od dołu do góry. Gdy dodasz `@parametrize` do miksu, kolejność argumentów
staje się nieoczywista i podatna na błędy:

```python
# NIEBEZPIECZNE — kolejność argumentów może być zła
@pytest.mark.parametrize("wartosci", [...])
@patch("app.main.settings")
async def test_health(mock_settings, wartosci):  # czy na pewno w tej kolejności?
    ...
```

Błąd który dostaniesz nie będzie oczywisty:
```
AttributeError: 'tuple' has no attribute 'is_dev'
```
Bo `mock_settings` jest w rzeczywistości krotką z `parametrize`, nie mockiem.

**Rozwiązanie — `patch` jako context manager wewnątrz funkcji:**

```python
@pytest.mark.parametrize("wartosci", [...])
async def test_health(wartosci):
    with patch("app.main.settings") as mock_settings:
        # mock_settings to na pewno mock
        # wartosci to na pewno wartosci z parametrize
        ...
```

`parametrize` zarządza argumentami funkcji. `patch` jest wewnątrz — nie miesza się
z argumentami. Zero konfliktu.

### Czym jest context manager

**Context manager** to obiekt, który mówi: „zrób coś przed wejściem do bloku `with` i coś po
wyjściu z niego". Kod „po wyjściu" wykona się **zawsze**, także gdy w środku poleci wyjątek,
dlatego context managery służą do zasobów, które trzeba zwolnić: pliki, połączenia, blokady.

```python
with open("data.txt") as file:      # wejście: plik otwarty
    content = file.read()
                                    # wyjście: plik zamknięty, nawet po błędzie
```

Przykłady, które pojawiają się w testach:

| Context manager | Co robi |
|---|---|
| `open(...)` | otwiera i zamyka plik |
| `smtplib.SMTP(...)`, `urlopen(...)` | zamykają połączenie |
| `pytest.raises(...)` | łapie wyjątek i sprawdza go |
| `patch(...)` | podmienia obiekt na czas bloku i przywraca go po wyjściu |

#### Jak to działa pod spodem

Obiekt ma dwie metody:

- `__enter__` uruchamia się przy wejściu, a jej wynik trafia do zmiennej po `as`,
- `__exit__` uruchamia się przy wyjściu, zawsze. Dostaje informację o wyjątku, a zwrócenie `True`
  go „połyka" (tak działa `pytest.raises`, gdy wyjątek jest oczekiwany).

Dlatego mock używany w `with` konfiguruje się przez
`mock.return_value.__enter__.return_value` — to obiekt, który `with` dostaje w zmiennej po `as`.

#### Własny context manager

Najprościej przez dekorator `@contextmanager` i `yield`:

```python
from contextlib import contextmanager

@contextmanager
def opened_file(path):
    file = open(path)
    try:
        yield file          # tu wykonuje się ciało bloku with
    finally:
        file.close()        # sprzątanie, zawsze
```

To ten sam schemat co **fixture z `yield`**: przygotowanie, `yield`, sprzątanie. Fixture to
w istocie context manager zarządzany przez pytest.

### Kiedy fixture zamiast `patch` jako context manager?

`patch` jako context manager wewnątrz funkcji — mock jest lokalny, tylko dla tego testu.
Fixture dla mocka ma sens tylko gdy:
- Ten sam mock jest reużywany w wielu **różnych** funkcjach testowych
- Chcesz wydzielić setup mocka w jedno miejsce

Gdy `parametrize` pokrywa wszystkie przypadki w jednej funkcji — fixture jest nadmiarowa.

#### Dwie wersje obok siebie

Context manager inline — patch widoczny tylko w bloku:

```python
def test_charge() -> None:
    with patch("src.shop.payment.urlopen") as mock_urlopen:
        ...
        gateway.charge(25.0, "anna@example.com")
    # po wyjściu z bloku patch jest już cofnięty
```

Fixture — patch aktywny w całym teście:

```python
@pytest.fixture
def mock_urlopen() -> Iterator[MagicMock]:
    with patch("src.shop.payment.urlopen") as mock:
        yield mock          # patch trwa przez cały test, potem jest cofnięty


def test_charge(mock_urlopen: MagicMock) -> None:
    gateway.charge(25.0, "anna@example.com")
```

W fixture z `yield` patch musi być **wewnątrz** `with`. Gdyby `yield` stał po zakończeniu bloku,
patch zostałby cofnięty, zanim test się zacznie.

#### Tabela wyboru

| Sytuacja | Wybór |
|---|---|
| Ten sam patch w **wielu różnych testach** | **fixture** |
| Patch ma działać przez **cały test** (mniej wcięć) | **fixture** |
| Mock jako **argument testu** z adnotacją typu | **fixture** |
| Ustawienia mocka (`return_value`, `side_effect`) wspólne dla grupy testów | **fixture** |
| Patch tylko dla **fragmentu testu** | **context manager** |
| Przygotowanie obiektów wymaga prawdziwej funkcji, a mock ma działać dopiero potem | **context manager** |
| Różne mocki w różnych fazach jednego testu | **context manager** |
| Jednorazowy, krótki test lub test z `parametrize` pokrywającym wszystkie przypadki | **context manager** (lub dekorator) |

#### Dekorator `@patch` i `monkeypatch`

- **Dekorator `@patch`** to trzecia droga, ale przy `parametrize` łatwo pomylić kolejność
  argumentów (patrz „Pułapka — `parametrize` + `patch` jako dekorator"). Fixture tego problemu nie
  ma, bo mocki są wstrzykiwane po nazwie.
- **`monkeypatch`** to wbudowana fixture pytesta: `monkeypatch.setattr("src.shop.payment.urlopen", fake)`.
  Podmiana jest cofana automatycznie po teście, bez `with`. Dobra do prostych podmian, ale nie daje
  mocka z asercjami typu `assert_called_once_with`.

---

## Asercje w pytest

pytest używa zwykłego `assert` z Pythona — nie ma specjalnych metod jak w `unittest`.
pytest automatycznie przechwytuje `assert` i pokazuje czytelny błąd gdy nie przejdzie.

### Porównania wartości

```python
assert x == y       # równość
assert x != y       # nierówność
assert x > y        # większy
assert x >= y       # większy lub równy
assert x < y        # mniejszy
assert x <= y       # mniejszy lub równy
```

### Prawdziwość

```python
assert x             # x jest truthy (nie None, nie 0, nie pusty)
assert not x         # x jest falsy
assert x is None     # x to dokładnie None
assert x is not None # x to nie None
assert x is True     # x to dokładnie True (nie tylko truthy)
```

### Kolekcje

```python
assert x in lista          # element jest w kolekcji
assert x not in lista      # element nie jest w kolekcji
assert len(lista) == 3     # długość kolekcji
assert lista == [1, 2, 3]  # porównanie całej listy

# słowniki
assert "klucz" in slownik           # klucz istnieje
assert slownik["klucz"] == "value"  # wartość pod kluczem
assert slownik == {"a": 1, "b": 2}  # porównanie całego słownika
```

### Wyjątki — `pytest.raises`

Sprawdzasz że funkcja **rzuca** wyjątek:

```python
with pytest.raises(ValueError):
    funkcja_ktora_powinna_rzucic()

# Sprawdzenie treści wyjątku
with pytest.raises(HTTPException) as exc_info:
    funkcja()

assert exc_info.value.status_code == 415
assert "not allowed" in exc_info.value.detail
```

#### Warianty

**Sam typ wyjątku** — najsłabsza forma, nie sprawdza komunikatu:

```python
with pytest.raises(ValueError):
    Product("Laptop", -1)
```

**`match`** — typ i komunikat. `match` jest **argumentem nazwanym** i działa jak
`re.search` (szuka dopasowania regex w tekście wyjątku):

```python
with pytest.raises(ValueError, match="Price cannot be negative"):
    Product("Laptop", -1)
```

> Pułapka: `pytest.raises(ValueError, "Price cannot be negative")` (bez `match=`) jest błędem.
> Drugi argument pozycyjny pytest traktuje jako funkcję do wywołania, więc kończy się
> `TypeError`, a nie sprawdzeniem komunikatu.

**`as excinfo`** — pełny dostęp do wyjątku, gdy chcesz sprawdzić więcej niż komunikat:

```python
with pytest.raises(ValueError) as excinfo:
    Product("Laptop", -1)

assert str(excinfo.value) == "Price cannot be negative"   # dokładne porównanie
assert excinfo.type is ValueError
```

Różnica: `match` szuka **podciągu** (regex), a `==` wymaga **dokładnego** tekstu.

**`re.escape`** — gdy komunikat zawiera znaki specjalne regex (`(`, `.`, `?`, `[`):

```python
with pytest.raises(KeyError, match=re.escape("Laptop is not in the cart")):
    cart.remove("Laptop")
```

**Kilka dopuszczalnych wyjątków** — krotka typów:

```python
with pytest.raises((ValueError, KeyError)):
    ...
```

#### Jedna instrukcja w bloku `with`

Wyjątek przerywa blok, więc w środku trzymaj **tylko tę jedną instrukcję**, która ma go rzucić.
Przygotowanie danych zrób przed blokiem — inaczej nie wiesz, która linia zgłosiła błąd:

```python
# źle — nie wiadomo, która linia rzuciła ValueError
with pytest.raises(ValueError):
    product = Product("Laptop", 10)
    product.remove_stock(5)

# dobrze
product = Product("Laptop", 10)
with pytest.raises(ValueError, match="Not enough stock"):
    product.remove_stock(5)
```

#### Typowe błędy w teście z `raises`

- **Pusty blok** (`...` albo `pass` w środku `with`) — nic nie rzuca wyjątku, test pada
  z `DID NOT RAISE`.
- **`match` bez nazwy** — patrz pułapka wyżej.
- **Brak `-> None`** w teście — mypy strict odrzuci commit.

#### Alternatywa: `try/except` + `pytest.fail` (nie polecana)

```python
try:
    Product("Laptop", -1)
except ValueError:
    pass
else:
    pytest.fail("ValueError not raised")
```

Działa, ale jest dłuższe i mniej czytelne niż `pytest.raises`. Z `unittest` znasz
`self.assertRaises` — w pytest używamy `pytest.raises`.

### Stringi

```python
assert "słowo" in tekst            # zawiera substring
assert tekst.startswith("prefix")  # zaczyna się od
assert tekst.endswith("suffix")    # kończy się na
```

### Typy

```python
assert isinstance(x, str)          # x jest stringiem
assert isinstance(x, (int, float)) # x jest int lub float
```

### Własna wiadomość błędu

Komunikat który pojawi się gdy asercja nie przejdzie:

```python
assert response["status"] == "ok", f"Oczekiwano 'ok', dostałem: {response['status']}"
```

### `pytest.approx` — porównanie liczb zmiennoprzecinkowych

Rozwiązuje problem niedokładności floatów:

```python
# Może nie przejść przez błąd zaokrąglenia
assert 0.1 + 0.2 == 0.3

# Przejdzie — approx dopuszcza małą tolerancję
assert 0.1 + 0.2 == pytest.approx(0.3)
```

### `pytest.warns` — sprawdzenie ostrzeżeń

Analogiczne do `pytest.raises` ale dla `warnings`:

```python
with pytest.warns(DeprecationWarning):
    stara_funkcja()
```

### `xfail` i `skip` — testy, które mają nie przechodzić albo nie działać

**`xfail`** oznacza test, który **powinien** padać (znany błąd lub niezaimplementowana funkcja).
Test jest uruchamiany, ale jego porażka nie psuje całego przebiegu:

```python
@pytest.mark.xfail(reason="Cart ignores quantity already in the cart", strict=True)
def test_cart_add_checks_total_stock() -> None:
    product = Product("Laptop", 10, stock=5)
    cart = Cart()
    cart.add(product, 3)
    with pytest.raises(ValueError, match="Not enough stock"):
        cart.add(product, 3)
```

Z `strict=True` test zacznie **padać (XPASS → FAILED)**, gdy naprawisz kod. Wtedy wiesz,
że trzeba zdjąć `xfail`. Bez `strict` taki test zostałby po cichu zaliczony.
Można też zawęzić do konkretnego wyjątku: `@pytest.mark.xfail(raises=ValueError)`.

**`skip` / `skipif`** — test w ogóle się nie uruchamia:

```python
@pytest.mark.skip(reason="not implemented yet")
def test_something() -> None: ...

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
def test_unix_paths() -> None: ...
```

| Marker | Test się uruchamia? | Użycie |
|---|---|---|
| `xfail` | Tak | Znany błąd, który ma być naprawiony |
| `skip` | Nie | Funkcja jeszcze nie istnieje |
| `skipif` | Nie, gdy warunek spełniony | Zależność od systemu lub wersji |

### Inne wbudowane narzędzia pytest

| Narzędzie | Do czego służy |
|---|---|
| `monkeypatch` | Podmiana atrybutu, funkcji lub zmiennej środowiskowej na czas testu (`monkeypatch.setattr`, `setenv`). Zmiany cofane automatycznie |
| `capsys` | Przechwytywanie tego, co kod wypisał przez `print` (`capsys.readouterr().out`) |
| `tmp_path` | Tymczasowy katalog unikalny dla testu, sprzątany automatycznie |
| `pytest.mark.<nazwa>` | Własne markery do grupowania testów; trzeba je zarejestrować w `pyproject.toml` (tu: `unit`) |

Uruchamianie wybranych testów po markerze: `pytest -m unit`. Wykluczanie: `pytest -m "not unit"`.

### Dlaczego pytest nie ma `assertEqual`, `assertIn` itp.?

Świadoma decyzja projektowa. pytest przepisuje bytecode `assert` podczas zbierania
testów — zwykły `assert x == y` przy błędzie pokazuje pełny diff:

```
assert {'status': 'ok', 'environment': 'dev'} == {'status': 'ok'}
  Left contains extra items: {'environment': 'dev'}
```

Biblioteka metod jak w `unittest` jest zbędna — `assert` daje tyle samo informacji.
Nie ma odpowiednika `assertEqual(actual, expected)` — używasz `assert actual == expected`.

---

## Mockowanie — unittest.mock

Mockowanie to zastępowanie prawdziwych zależności (baza, API, czas) fałszywymi obiektami,
które kontrolujesz w teście.

### Kiedy używać?

Gdy testowana funkcja wywołuje coś zewnętrznego — bazę, HTTP request, zapis do pliku.
Nie chcesz żeby test faktycznie to robił — chcesz kontrolować co "zewnętrzny system" zwraca.

### Typy mocków

| Typ | Kiedy używać |
|-----|-------------|
| `MagicMock` | synchroniczne obiekty i metody |
| `AsyncMock` | async metody (`await`) |

#### MagicMock

Fałszywy obiekt który przyjmuje dowolne wywołania metod i atrybutów, zapamiętuje jak był wywoływany i pozwala ustawić co ma zwracać.

```python
from unittest.mock import MagicMock

repo = MagicMock()
repo.znajdz_uzytkownika.return_value = {"id": 1, "imie": "Jan"}

wynik = repo.znajdz_uzytkownika(id=1)
assert wynik["imie"] == "Jan"
repo.znajdz_uzytkownika.assert_called_once_with(id=1)
```

#### AsyncMock

Jak `MagicMock` ale dla metod które wymagają `await`. Zwykły `MagicMock` nie jest awaitable — użycie go z `await` rzuci `TypeError`.

```python
from unittest.mock import AsyncMock, MagicMock

file = MagicMock()           # sam obiekt — sync
file.read = AsyncMock()      # metoda read — async, wymaga await
```

#### `spec=` — ograniczenie do interfejsu klasy

Bez `spec` mock przyjmuje dowolne atrybuty i metody, nawet nieistniejące. Z `spec` pozwala tylko na to co faktycznie istnieje w klasie:

```python
from sqlalchemy.ext.asyncio import AsyncSession

session = AsyncMock(spec=AsyncSession)
session.flush()       # OK — AsyncSession ma flush
session.nieistniejace()  # AttributeError — nie ma takiej metody
```

Stosuj `spec` przy mockach sesji bazodanowej — test wykryje literówki w nazwach metod.

---

### Parametry mock — `return_value` vs `side_effect`

#### `return_value`

Mock zawsze zwraca tę samą wartość, bez względu na liczbę wywołań:

```python
mock.read = AsyncMock(return_value=b"dane")
await mock.read()  # → b"dane"
await mock.read()  # → b"dane"  (zawsze to samo)
```

Gdy podasz listę jako `return_value` — zwróci **całą listę** jako pojedynczą wartość, nie będzie po niej iterować:

```python
mock.read = AsyncMock(return_value=[b"chunk", b""])
await mock.read()  # → [b"chunk", b""]  (lista, nie b"chunk")
```

#### `side_effect` z listą

Mock zwraca kolejne elementy listy przy każdym wywołaniu:

```python
mock.read = AsyncMock(side_effect=[b"chunk1", b"chunk2", b""])
await mock.read()  # → b"chunk1"
await mock.read()  # → b"chunk2"
await mock.read()  # → b""
await mock.read()  # → StopAsyncIteration
```

Idealny do symulacji strumieni i paginacji — każde wywołanie zwraca następny kawałek danych, `b""` sygnalizuje koniec.

#### `side_effect` z wyjątkiem

Mock rzuca wyjątek przy wywołaniu:

```python
mock.read = AsyncMock(side_effect=IOError("disk full"))
await mock.read()  # → rzuca IOError
```

Stosuj gdy testujesz obsługę błędów.

#### Zasada wyboru

| Scenariusz | Co użyć |
|------------|---------|
| Zawsze ten sam wynik | `return_value` |
| Koniec strumienia / różne odpowiedzi | `side_effect` z listą |
| Testowanie obsługi błędów | `side_effect` z wyjątkiem |

---

### Rozpakowywanie `side_effect` w teście

Gdy `side_effect` jest listą i chcesz wyciągnąć wartości do asercji — rozpakowujesz jak zwykłą listę:

```python
side_effect = [b"%PDF content", b""]
content_value, _ = side_effect   # content_value = b"%PDF content", _ = b""
```

Gwiazdka po lewej stronie zbiera resztę elementów:

```python
first, *rest = [b"a", b"b", b"c"]  # first = b"a", rest = [b"b", b"c"]
content_value, *_ = side_effect    # content_value = b"%PDF content", _ = [b""]
```

Gwiazdka po prawej stronie — wstawia elementy do nowej kolekcji:

```python
a = [1, 2]
b = [*a, 3, 4]   # → [1, 2, 3, 4]
f(*a)            # → f(1, 2)
```

---

### patch

`patch` podmienia obiekt w module na czas testu i przywraca oryginał po zakończeniu.

```python
from unittest.mock import patch

def test_pobierz_dane():
    with patch("modul.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        wynik = pobierz_dane("https://api.example.com")
        assert wynik["status"] == "ok"
```

Patchuj tam gdzie obiekt jest **używany**, nie gdzie jest zdefiniowany:

```python
patch("app.main.settings")      # dobrze — tam gdzie używany
patch("app.config.settings")    # źle — tam gdzie zdefiniowany, main.py tego nie zobaczy
```

### Asercje na mockach — weryfikacja wywołań

Mock nie tylko zastępuje obiekt — zapamiętuje jak był wywoływany. Po wykonaniu testowanej
funkcji możesz zapytać mocka czy jego metody zostały wywołane i z jakimi argumentami.

```python
mock_session.add.assert_called_once()           # wywołano dokładnie raz, argument nieważny
mock_session.add.assert_called_once_with(user)  # wywołano dokładnie raz z tym argumentem
mock_session.flush.assert_called_once()         # flush wywołano dokładnie raz
```

Przykład dla `create_user`:

```python
async def test_create_user(mock_session):
    data = UserCreate(first_name="Jan", last_name="Kowalski", email="jan@example.com")
    await create_user(mock_session, data)

    mock_session.add.assert_called_once()             # sprawdza że add() zostało wywołane
    mock_session.flush.assert_called_once()           # sprawdza że flush() zostało wywołane
```

Pełna tabela metod asercji:

| Metoda | Co sprawdza |
|--------|-------------|
| `assert_called_once()` | wywołano dokładnie raz, argument nieważny |
| `assert_called_once_with(x)` | wywołano dokładnie raz z argumentem `x` |
| `assert_called()` | wywołano co najmniej raz |
| `assert_not_called()` | nie wywołano ani razu |
| `assert_called_with(x)` | ostatnie wywołanie miało argument `x` |

Asercje na wywołaniach mają sens gdy **efektem ubocznym** funkcji jest wywołanie
zależności — np. zapis do bazy, wysłanie emaila, zapis do pliku. Weryfikujesz wtedy
nie tylko wynik (`return`) ale też że kod faktycznie wykonał oczekiwaną operację.

### Mockowanie zależności wstrzykiwanych przez konstruktor

Gdy klasa dostaje swoje zależności w konstruktorze (`OrderService(gateway, notifier)`), nie
potrzebujesz `patch` — wystarczy przekazać mock zamiast prawdziwego obiektu.

```python
from unittest.mock import create_autospec

@pytest.fixture
def gateway() -> PaymentGateway:
    mock = create_autospec(PaymentGateway, instance=True)
    mock.charge.return_value = "tx-1"
    return mock
```

**`create_autospec(Klasa, instance=True)` zamiast `Mock(spec=Klasa)`:**

| | `Mock(spec=Klasa)` | `create_autospec(Klasa, instance=True)` |
|---|---|---|
| Odrzuca nieistniejące metody i atrybuty | tak | tak |
| Sprawdza **sygnaturę** wywołań (liczbę i nazwy argumentów) | nie | tak |
| Typ widziany przez mypy | `Mock` — niezgodny z parametrem `PaymentGateway` | `Any` — przechodzi |

Autospec łapie błędy w teście, np. `gateway.charge(1, 2, 3)` przy metodzie z dwoma argumentami, a
przy okazji nie wymaga `cast` w trybie mypy strict.

> Atrybuty ustawiane w `__init__` (np. `base_url`) nie należą do klasy, więc `spec` ich nie widzi
> — odwołanie do nich w mocku rzuci `AttributeError`. Ustaw je ręcznie albo mockuj tylko metody.

**Scenariusze dla `OrderService.checkout`:**

```python
def test_checkout_happy_path(gateway, notifier, order) -> None:
    service = OrderService(gateway, notifier)

    assert service.checkout(order) == "tx-1"
    gateway.charge.assert_called_once_with(order.total(), order.customer.email)
    notifier.send_order_confirmation.assert_called_once_with(order)
    assert order.status == "paid"


def test_checkout_payment_failure(gateway, notifier, order) -> None:
    gateway.charge.side_effect = PaymentError("Payment declined: no funds")

    with pytest.raises(PaymentError, match="declined"):
        OrderService(gateway, notifier).checkout(order)

    assert order.status == "new"                          # zamówienie nietknięte
    notifier.send_order_confirmation.assert_not_called()  # nic nie wysłano
```

Test **błędu zależności** sprawdza trzy rzeczy: że wyjątek propaguje, że stan obiektu się nie
zmienił i że kolejne kroki (powiadomienie) się nie wykonały.

### Mockowanie wywołania z menedżerem kontekstu (`with ... as`)

`urlopen` i `smtplib.SMTP` są używane jako `with urlopen(...) as response:`. `MagicMock`
obsługuje `__enter__` i `__exit__`, ale obiekt użyty w `with` to **`return_value.__enter__.return_value`**,
a nie sam mock:

```python
@patch("src.shop.payment.urlopen")
def test_charge_approved(mock_urlopen: MagicMock) -> None:
    response = mock_urlopen.return_value.__enter__.return_value
    response.read.return_value = b'{"status": "approved", "transaction_id": "tx-1"}'

    gateway = PaymentGateway("https://pay.example.com", "secret")

    assert gateway.charge(25.0, "anna@example.com") == "tx-1"
```

- `patch("src.shop.payment.urlopen")` — patchujemy tam, gdzie nazwa jest **używana**
  (`payment.py` robi `from urllib.request import urlopen`).
- `json.load(response)` woła `response.read()`, więc wystarczy ustawić `read.return_value` na bajty.

**Sprawdzanie, co zostało wysłane** — pierwszy argument `urlopen` to obiekt `Request`:

```python
request = mock_urlopen.call_args.args[0]

assert request.full_url == "https://pay.example.com/charges"
assert request.get_method() == "POST"
assert request.get_header("Authorization") == "Bearer secret"
assert json.loads(request.data) == {"amount": 25.0, "email": "anna@example.com"}
assert mock_urlopen.call_args.kwargs["timeout"] == 5.0
```

Nagłówki są zapisywane z pierwszą wielką literą i resztą małych (`Content-type`), więc
`get_header("Content-Type")` zwróci `None` — użyj `get_header("Content-type")`.

**Błąd sieci:** `side_effect` z wyjątkiem zamiast `return_value`:

```python
mock_urlopen.side_effect = URLError("connection refused")
with pytest.raises(PaymentError, match="unavailable"):
    gateway.charge(25.0, "anna@example.com")
```

**Walidacja przed wywołaniem:** gdy kod odrzuca dane zanim sięgnie do sieci, sprawdź
`mock_urlopen.assert_not_called()`.

**SMTP:**

```python
@patch("src.shop.notifications.smtplib.SMTP")
def test_send(mock_smtp: MagicMock) -> None:
    EmailNotifier("smtp.example.com", 587).send("anna@example.com", "Hi", "Body")

    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    server = mock_smtp.return_value.__enter__.return_value
    message = server.send_message.call_args.args[0]
    assert message["To"] == "anna@example.com"
    assert message["Subject"] == "Hi"
```

### Dodatkowe informacje o wywołaniach mocka

| Atrybut | Co zwraca |
|---|---|
| `mock.call_args` | ostatnie wywołanie; `.args` (krotka) i `.kwargs` (słownik) |
| `mock.call_args_list` | lista wszystkich wywołań |
| `mock.call_count` | liczba wywołań |
| `mock.assert_has_calls([call(1), call(2)])` | wywołania z tymi argumentami, w tej kolejności |
| `mock.reset_mock()` | czyści historię wywołań |

`call_args.args[0]` jest potrzebne, gdy argumentem jest obiekt zbudowany wewnątrz testowanego
kodu (jak `Request` czy `EmailMessage`) — nie możesz go porównać `assert_called_once_with`, bo nie
masz do niego referencji.

### Sprawdzanie logów — `caplog`

Kod, który **łapie błąd i loguje ostrzeżenie** zamiast go przepuszczać, testujesz fixture `caplog`:

```python
def test_checkout_survives_email_failure(gateway, notifier, order, caplog) -> None:
    notifier.send_order_confirmation.side_effect = smtplib.SMTPException("server down")

    with caplog.at_level(logging.WARNING):
        transaction_id = OrderService(gateway, notifier).checkout(order)

    assert transaction_id == "tx-1"
    assert order.status == "paid"
    assert f"Could not send confirmation to {order.customer.email}" in caplog.messages
```

- `caplog.messages` — lista sformatowanych komunikatów, `caplog.records` — pełne obiekty
  (poziom, nazwa loggera).
- `caplog.at_level(...)` ustawia poziom na czas bloku; bez niego ostrzeżenia mogą nie trafić do
  przechwytywania, zależnie od konfiguracji.

### Złota zasada mockowania

Mockuj na granicy systemu — tam gdzie Twój kod "wychodzi na zewnątrz".
Nie mockuj wewnętrznych funkcji swojego własnego kodu.

---

## Testowanie wczytywania plików (txt, json, csv)

### Zasada: prawdziwy plik w `tmp_path`, nie mock

Dla kodu czytającego pliki najlepiej utworzyć **prawdziwy plik** w katalogu tymczasowym. Test
sprawdza wtedy też obsługę kodowania, nowych linii i błędów systemu plików, a nie tylko Twoje założenia.
`tmp_path` to `pathlib.Path` unikalny dla testu i sprzątany automatycznie.

```python
def test_read_lines_skips_comments_and_blanks(tmp_path: Path) -> None:
    file = tmp_path / "notes.txt"
    file.write_text("# comment\n\nfirst\n  second  \n", encoding="utf-8")

    assert read_lines(file) == ["first", "second"]
```

> **Zawsze podawaj `encoding="utf-8"` przy zapisie.** Bez niego `write_text` używa kodowania
> systemowego (na Windows zwykle cp1252), a `read_text(encoding="utf-8")` w testowanym kodzie
> przeczyta inne bajty — test przejdzie lub padnie zależnie od systemu.

Na Windows `write_text` zamienia `\n` na `\r\n`. Jeśli potrzebujesz dokładnych bajtów, użyj
`write_bytes(b"...")` albo `write_text(..., newline="\n")`.

### Fixture z gotowym plikiem

Gdy kilka testów potrzebuje tego samego pliku, zrób z niego fixture:

```python
@pytest.fixture
def products_csv(tmp_path: Path) -> Path:
    file = tmp_path / "products.csv"
    file.write_text("name,price,stock\nBattery,10.25,5\nCable,4.99,\n", encoding="utf-8")
    return file


def test_load_from_csv(products_csv: Path) -> None:
    products = ProductImporter().load_from_csv(products_csv)

    assert [(p.name, p.price, p.stock) for p in products] == [("Battery", 10.25, 5), ("Cable", 4.99, 0)]
```

### Co testować przy każdym formacie

| Format | Przypadki |
|---|---|
| **txt** | pusty plik, same komentarze i puste linie, białe znaki na końcach, znaki spoza ASCII, brak pliku |
| **json** | poprawny obiekt i lista, niepoprawny JSON (`match="Invalid JSON"`), pusty plik, zły typ danych na górze (obiekt zamiast listy) |
| **csv** | poprawny plik, tylko nagłówek (zwraca `[]`), pusty plik, brakująca kolumna, inny separator (`;`), pusty element (np. brak `stock`), niepoprawna liczba |

Brak pliku to `FileNotFoundError`, którego kod nie przechwytuje, więc test sprawdza po prostu to:

```python
def test_read_text_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_text(tmp_path / "missing.txt")
```

### `parametrize` dla zawartości plików

Wiele wariantów zawartości w jednym teście:

```python
@pytest.mark.parametrize(
    ("content", "expected"),
    [
        pytest.param("", [], id="empty"),
        pytest.param("# only comment\n", [], id="only-comments"),
        pytest.param("a\n\nb\n", ["a", "b"], id="blank-lines"),
        pytest.param("  a  \n", ["a"], id="whitespace"),
        pytest.param("zażółć\n", ["zażółć"], id="non-ascii"),
    ],
)
def test_read_lines(tmp_path: Path, content: str, expected: list[str]) -> None:
    file = tmp_path / "data.txt"
    file.write_text(content, encoding="utf-8")

    assert read_lines(file) == expected
```

Jedna funkcja pomocnicza do zapisu pliku zmniejsza powtórzenia, gdy w pliku testów jest ich wiele.

### Błędy w plikach — `pytest.raises` z `match`

```python
def test_read_json_invalid(tmp_path: Path) -> None:
    file = tmp_path / "bad.json"
    file.write_text("{not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        read_json(file)


def test_read_csv_missing_column(tmp_path: Path) -> None:
    file = tmp_path / "products.csv"
    file.write_text("name\nBattery\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing columns: price"):
        read_csv(file, required_columns=("name", "price"))
```

W `match` nie podawaj pełnej ścieżki do pliku — `tmp_path` jest inny przy każdym uruchomieniu.
Dopasuj tylko stałą część komunikatu.

### Trzy sposoby odizolowania od dysku

| Sposób | Kiedy | Uwagi |
|---|---|---|
| **`tmp_path` + prawdziwy plik** | domyślnie, dla czytników plików | najmniej założeń, działa tak jak w produkcji |
| **`patch` na funkcji czytającej** | testujesz logikę *nad* czytnikiem (np. `ProductImporter`) | szybki, ale test nie sprawdza integracji z czytnikiem |
| **`mock_open`** | kod używa wbudowanego `open()` i nie możesz zmienić ścieżki | kruchy: test zależy od tego, *jak* kod czyta plik |

Przykład z `patch` — logika importera bez dotykania dysku:

```python
@patch("src.shop.importer.read_csv")
def test_importer_builds_products(mock_read_csv: MagicMock) -> None:
    mock_read_csv.return_value = [{"name": "Battery", "price": "10.25", "stock": ""}]

    products = ProductImporter().load_from_csv("ignored.csv")

    assert products[0].stock == 0
    mock_read_csv.assert_called_once_with("ignored.csv", required_columns=("name", "price"))
```

Test ze `tmp_path` jest jednak pewniejszy. `patch` ma sens, gdy chcesz **wymusić** wynik, który trudno
uzyskać z prawdziwego pliku, albo przetestować warstwę wyżej niezależnie od niższej.

### Pliki z katalogu `data/`

Przykładowe pliki w `data/` nadają się do **jednego** testu „na prawdziwych danych":

```python
DATA_DIR = Path(__file__).parents[2] / "data"

def test_load_sample_products() -> None:
    products = ProductImporter().load_from_csv(DATA_DIR / "products.csv")

    assert len(products) == 3
```

Ścieżkę buduj względem pliku testowego (`__file__`), a nie względem bieżącego katalogu, bo
`pytest` można uruchomić z dowolnego miejsca. Testy ze stałymi plikami są jednak powiązane z ich
zawartością — zmiana pliku psuje test, więc większość przypadków trzymaj w `tmp_path`.

Jeśli kod używa ścieżek względnych, `monkeypatch.chdir(tmp_path)` zmienia bieżący katalog na czas
testu i przywraca go po jego zakończeniu.

---

## TDD — Test Driven Development

Podejście do pisania kodu gdzie **test powstaje przed implementacją**.

### Cykl Red → Green → Refactor

```
Red     →  napisz test który PADA (bo kodu jeszcze nie ma)
Green   →  napisz minimalny kod żeby test PRZESZEDŁ
Refactor → popraw kod nie łamiąc testów
```

I powtarzaj.

### Dlaczego to działa?

- Zmusza Cię do przemyślenia interfejsu funkcji *zanim* ją napiszesz
- Gwarantujesz 100% pokrycie — każda linia kodu istnieje bo był dla niej test
- Testy są pisane gdy rozumiesz wymagania, nie po fakcie

### Kiedy TDD ma sens, a kiedy nie?

| TDD ma sens | TDD ma mniejszy sens |
|-------------|----------------------|
| Logika biznesowa | Eksploracja / prototypowanie |
| Algorytmy | Glue code / konfiguracja |
| Funkcje z jasno zdefiniowanymi wymaganiami | Integracje z zewnętrznymi systemami |

### Czy musimy stosować TDD?

Nie. TDD to narzędzie, nie dogmat. Można pisać dobre testy bez TDD.
Warto jednak znać cykl — pomaga myśleć o kodzie testowalnie.

---

## Testy mutacyjne (Mutation Testing)

Technika sprawdzająca **jakość Twoich testów**, nie jakość kodu.

### Problem który rozwiązują

Możesz mieć 100% pokrycia kodu testami, a mimo to mieć słabe testy. Pokrycie mówi tylko
czy dana linia była wykonana — nie czy test *naprawdę* ją sprawdza.

Przykład słabego testu:

```python
def czy_pelnoletni(wiek):
    return wiek >= 18

def test_pelnoletni():
    wynik = czy_pelnoletni(20)
    assert wynik == True  # przechodzi, ale nie sprawdza granicy
```

Ten test przejdzie nawet jeśli zmienisz `>= 18` na `>= 0`.

### Jak działają?

Narzędzie automatycznie **wprowadza małe błędy** (mutacje) do kodu produkcyjnego, np.:

| Oryginał | Mutacja |
|----------|---------|
| `wiek >= 18` | `wiek > 18` |
| `return True` | `return False` |
| `a + b` | `a - b` |
| `if x:` | `if not x:` |

Potem uruchamia Twoje testy na zmutowanym kodzie:

- Testy **padły** → mutant zabity ✓ (testy są czujne)
- Testy **przeszły** → mutant przeżył ✗ (testy nie wykryły błędu)

### Wynik — Mutation Score

```
Mutation Score = zabite mutanty / wszystkie mutanty * 100%
```

Im wyższy wynik, tym lepsze testy. Cel to zazwyczaj **80–90%**, nie 100%
(niektóre mutanty są z natury nieistotne).

### Skąd mutmut wie jak modyfikować kod?

mutmut nie rozumie logiki biznesowej — stosuje **z góry zdefiniowany zestaw reguł mutacji**.
To mechaniczne zamiany które symulują typowe błędy programisty.

| Kategoria | Oryginał | Mutacja |
|-----------|----------|---------|
| Operatory porównania | `>=` | `>` |
| Operatory porównania | `==` | `!=` |
| Operatory arytmetyczne | `+` | `-` |
| Operatory arytmetyczne | `*` | `/` |
| Operatory logiczne | `and` | `or` |
| Wartości logiczne | `True` | `False` |
| Warunki | `if x:` | `if not x:` |
| Liczby | `18` | `19` |
| Stringi | `"ok"` | `"XX"` |

mutmut skanuje kod, znajduje każde miejsce gdzie można zastosować regułę
i tworzy osobną wersję pliku dla każdej mutacji.

### Jak pisać testy pod mutmut?

Nie piszesz osobnych testów dla mutmut — piszesz zwykłe testy pytest.
mutmut je tylko ocenia. Dobre praktyki:

**Testuj wartości graniczne:**

```python
# Słaby — mutant wiek > 18 przeżyje
assert czy_pelnoletni(20) == True

# Dobry — mutant wiek > 18 padnie
assert czy_pelnoletni(18) == True   # granica
assert czy_pelnoletni(17) == False  # tuż poniżej
```

**Sprawdzaj konkretne wartości, nie tylko prawdziwość:**

```python
# Słaby
assert dodaj(2, 3) > 0

# Dobry
assert dodaj(2, 3) == 5
```

**Testuj każdą ścieżkę logiczną:**

```python
def test_status_ok():
    assert oblicz_status(100) == "ok"

def test_status_blad():
    assert oblicz_status(-1) == "blad"
```

### Narzędzie w Pythonie — mutmut

Instalacja (projekt używa uv):

```bash
uv add --dev mutmut
```

Konfiguracja w `pyproject.toml`:

```toml
[tool.mutmut]
paths_to_mutate = "app/"
runner = "pytest"
tests_dir = "tests/"
```

Użycie:

```bash
mutmut run        # uruchamia mutacje
mutmut results    # pokazuje wyniki
mutmut show 5     # pokazuje konkretnego mutanta
```

Cały flow:

```
Ty piszesz testy w pytest
        ↓
mutmut mutuje kod produkcyjny
        ↓
mutmut odpala pytest na zmutowanym kodzie
        ↓
mutmut raportuje które mutanty przeżyły (= słabe miejsca w testach)
        ↓
Ty patrzysz na raport i dopisujesz brakujące asercje
```

### Jak często uruchamiać?

| Sytuacja | Częstotliwość |
|----------|---------------|
| Lokalne TDD / bieżąca praca | Nie uruchamiaj |
| Po napisaniu testów dla modułu | Raz, żeby ocenić jakość |
| Przed merge'em ważnej logiki | Opcjonalnie |
| CI/CD — każdy PR | Zbyt kosztowne, nie rób tego |
| CI/CD — scheduled job (np. raz w tygodniu) | To ma sens |

Powód: mutmut uruchamia pytest osobno dla każdej mutacji.
Przy 300 mutantach i suite trwającej 10s = 50 minut na jeden run.

### Kiedy warto używać?

- Gdy masz już testy i chcesz ocenić ich **realną wartość**
- Przy krytycznej logice biznesowej
- Nie na co dzień — narzędzie diagnostyczne, nie codzienny workflow

---

## Testy integracyjne — teoria

### Czym różnią się od unit testów?

W unit testach izolujesz i mockujesz wszystko co zewnętrzne. W integration testach robisz
odwrotnie — **używasz prawdziwych komponentów** i sprawdzasz czy ze sobą współpracują.

| | Unit test | Integration test |
|--|-----------|-----------------|
| Baza danych | Mock | Prawdziwa (testowa) |
| HTTP request | Mock | Prawdziwy klient testowy |
| System plików | Mock | Prawdziwy (tymczasowy) |
| Szybkość | Milisekundy | Sekundy |
| Cel | Logika funkcji | Współpraca komponentów |

### Co testują integration testy w FastAPI?

Główne pytania które zadajesz:

- Czy endpoint zwraca właściwy status HTTP?
- Czy request/response mają właściwy kształt (schema)?
- Czy dane faktycznie trafiają do bazy / na dysk?
- Czy middleware, dependency injection, autoryzacja działają razem?

---

## TestClient

`TestClient` (oparty na `httpx`) wysyła prawdziwe requesty do aplikacji przez cały stack —
routing, middleware, dependency injection, walidację Pydantic — bez uruchamiania
prawdziwego serwera HTTP. Działa synchronicznie nawet jeśli endpointy są `async`.

### Jak działa pod spodem — ASGI

FastAPI jest aplikacją **ASGI** (Asynchronous Server Gateway Interface) — standardu
który definiuje jak serwer HTTP komunikuje się z aplikacją Python.

Normalny flow produkcyjny:
```
Przeglądarka / klient HTTP
        ↓
Serwer ASGI (uvicorn)
        ↓
Aplikacja FastAPI
```

TestClient eliminuje `uvicorn` z równania — wywołuje aplikację ASGI bezpośrednio
w pamięci zamiast otwierać socket sieciowy:

```
TestClient
        ↓
Aplikacja FastAPI (bezpośrednio)
```

Dlatego nie potrzebujesz uruchomionego serwera, otwartego portu ani połączenia sieciowego.

### Dlaczego synchroniczny mimo async FastAPI

TestClient jest synchroniczny — wywołujesz `client.get(...)` i od razu dostajesz wynik
bez `await`. Starlette wewnętrznie uruchamia event loop który wykonuje async kod
i blokuje aż do odpowiedzi. Z perspektywy testu to zwykłe synchroniczne wywołanie.

### Co przechodzi przez TestClient

Mimo braku serwera — przez TestClient przechodzi **pełny stack aplikacji**:

```
TestClient.get("/health")
        ↓
Middleware FastAPI
        ↓
Router (dopasowanie URL i metody HTTP)
        ↓
Dependency Injection (Depends())
        ↓
Walidacja Pydantic
        ↓
Funkcja endpointu
        ↓
Serializacja response do JSON
        ↓
httpx.Response
```

### Co NIE przechodzi przez TestClient

- Sieć (TCP/IP) — nie ma połączenia sieciowego
- Sockety i porty — nie są używane
- TLS/SSL — nie ma szyfrowania

Dla celów testów to nie ma znaczenia — te warstwy są domeną infrastruktury,
nie kodu aplikacji.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
```

`TestClient` można skonfigurować przez fixture pytest ze `scope="session"` — aplikacja
startuje raz dla całego zestawu testów, nie dla każdego testu osobno. Ważne gdy startup
jest kosztowny (połączenie z bazą, cache itp.).

`TestClient` obsługuje:
- wszystkie metody HTTP (`get`, `post`, `put`, `patch`, `delete`, `head`, `options`)
- query params (`params={"skip": 0}`)
- JSON body (`json={...}`)
- form data (`data={...}`)
- pliki multipart (`files={"file": ("nazwa.pdf", bytes_content, "application/pdf")}`)
- nagłówki per request i domyślne dla całego klienta (`headers={...}`)
- cookies (`cookies={...}`)
- lifecycle aplikacji przez context manager (`with TestClient(app) as client`)
- scope fixture: `function` (domyślne), `module`, `session`

Każde wywołanie zwraca `httpx.Response` z polami:
- `response.status_code` — kod HTTP
- `response.json()` — body jako dict
- `response.text` — body jako string
- `response.content` — body jako bytes
- `response.headers` — nagłówki odpowiedzi
- `response.cookies` — cookies z odpowiedzi

### Metody HTTP — szczegółowo

```python
client.get("/health")
client.post("/upload")
client.put("/items/1")
client.patch("/items/1")
client.delete("/items/1")
client.head("/health")
client.options("/health")
```

### Przekazywanie danych — szczegółowo

**Query params:**
```python
client.get("/items", params={"skip": 0, "limit": 10})
# → GET /items?skip=0&limit=10
```

**JSON body:**
```python
client.post("/items", json={"name": "test", "price": 9.99})
```

**Form data:**
```python
client.post("/login", data={"username": "jan", "password": "haslo"})
```

**Pliki (multipart/form-data):**
```python
client.post("/upload", files={"file": ("nazwa.pdf", bytes_content, "application/pdf")})
# krotka: (nazwa_pliku, zawartość, content_type)
```

**Pliki + dane jednocześnie:**
```python
client.post("/upload",
    files={"file": ("doc.pdf", content, "application/pdf")},
    data={"description": "mój dokument"}
)
```

#### `multipart/form-data` — jak wygląda request pod spodem

HTTP request ma `body` i `headers`. `Content-Type` w nagłówku mówi serwerowi jak interpretować body.

Trzy główne warianty dla POST:

| Content-Type | Używany do | Wygląd body |
|---|---|---|
| `application/json` | API, dane strukturalne | `{"name": "test"}` |
| `application/x-www-form-urlencoded` | proste formularze HTML | `name=test&age=5` |
| `multipart/form-data` | pliki + dane mieszane | wiele sekcji z boundary |

`multipart` znaczy dosłownie "wiele części". Body jest podzielone na sekcje separatorem zwanym **boundary**:

```
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf

%PDF-1.4 1 0 obj<</Type/Catalog>>endobj
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

Każda część ma własne nagłówki i własne body. Dlatego można w jednym requeście wysłać i plik i pole tekstowe jako osobne części.

FastAPI odczytuje `UploadFile` **wyłącznie** z `multipart/form-data` — stąd `files=` jest jedyną poprawną opcją przy testowaniu endpointów przyjmujących pliki.

#### Parametr `files=` — wymagane i opcjonalne

```python
files={
    "klucz": (filename, content, content_type, headers)
}
```

Klucz słownika — **wymagany** — nazwa pola formularza, musi zgadzać się z parametrem endpointu (`File(...)` w `UploadValidator.__init__`).

Z tych elementów `httpx` buduje nagłówek części:
```
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf
```

Wartość — krotka z 1 do 4 elementów:

| Element krotki | Wymagany | Co robi |
|----------------|----------|---------|
| `content` | tak | bajty lub file-like object (`BytesIO`, otwarty plik) |
| `filename` | nie | pojawia się w `Content-Disposition`; dostępny jako `UploadFile.filename`; bez niego FastAPI ustawi `None` |
| `content_type` | nie | trafia do `Content-Type` części; bez niego httpx ustawi `application/octet-stream`; dostępny jako `UploadFile.content_type` |
| `headers` | nie | dodatkowe nagłówki tej części (rzadko potrzebne) |

Skrócona forma — samo `content` bez krotki:
```python
files={"file": b"raw bytes"}  # filename=None, content_type=application/octet-stream
```

Dlaczego nie `data=` ani `json=`:
```python
# application/x-www-form-urlencoded — FastAPI nie dostanie UploadFile
test_client.post("/upload", data={"file": sample_pdf})

# application/json — nie obsługuje danych binarnych
test_client.post("/upload", json={"file": "..."})
```

### Nagłówki — szczegółowo

```python
# per request
client.get("/protected", headers={"Authorization": "Bearer token123"})

# domyślne dla całego klienta
client = TestClient(app, headers={"Authorization": "Bearer token123"})
```

### Obiekt Response — szczegółowo

```python
response = client.get("/health")

response.status_code               # 200, 404, 415...
response.json()                    # parsuje body jako dict
response.text                      # body jako string
response.content                   # body jako bytes
response.headers                   # słownik nagłówków
response.headers["content-type"]   # konkretny nagłówek
response.cookies                   # cookies z response
```

### Kontekst manager — lifecycle aplikacji

Jeśli aplikacja ma eventy `startup` / `shutdown` — użyj `TestClient` jako context manager:

```python
with TestClient(app) as client:
    response = client.get("/health")
# po wyjściu z bloku — shutdown event odpala się
```

Bez `with` — eventy startup/shutdown nie są wywoływane.

### Obsługa błędów HTTP

Domyślnie `TestClient` nie rzuca wyjątku gdy aplikacja zwróci błąd HTTP (404, 500).
Dostajesz response z odpowiednim `status_code` — sprawdzasz go asercją:

```python
response = client.post("/upload")  # brak pliku
assert response.status_code == 422
```

### Scope fixture — szczegółowo

```python
@pytest.fixture(scope="function")  # domyślne — nowy klient dla każdego testu
@pytest.fixture(scope="module")    # jeden klient na plik testowy
@pytest.fixture(scope="session")   # jeden klient na całą sesję testową
```

Im szerszy scope tym szybsze testy — ale uwaga na współdzielony stan między testami.

---

## TestClient vs AsyncClient — problem event loop

### Kiedy TestClient nie wystarczy

`TestClient` jest synchroniczny — Starlette uruchamia aplikację ASGI w osobnym wątku z własnym event loop. Działa dobrze gdy testy są proste i nie współdzielą zasobów async z aplikacją.

Problem pojawia się gdy fixture `db_session` tworzy połączenie async w event loop pytest-asyncio, a `TestClient` próbuje go użyć w swoim własnym event loop. Asyncpg (i ogólnie asyncio) nie pozwala na użycie połączenia między różnymi event loopami:

```
RuntimeError: Task got Future attached to a different loop
```

Sytuacja która to wywołuje:

```
pytest-asyncio event loop
    └── fixture db_session → AsyncConnection (loop A)
                                    ↓ override_get_db podaje sesję do aplikacji
TestClient (własny event loop B)
    └── endpoint → session.flush() → asyncpg operacja → loop A ≠ loop B → BŁĄD
```

Insert faktycznie trafia do bazy (widać `BEGIN` i SQL w logach), ale odpowiedź nie wraca — asyncpg nie może zwrócić wyniku do innego loopa.

### Rozwiązanie — AsyncClient z httpx

`AsyncClient` z `httpx` nie tworzy osobnego wątku — wywołuje aplikację ASGI bezpośrednio w tym samym event loop co fixture:

```
pytest-asyncio event loop (jeden)
    └── fixture db_session → AsyncConnection
    └── AsyncClient → endpoint → session.flush() → asyncpg → ten sam loop → OK
```

Implementacja w `conftest.py`:

```python
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()
```

`ASGITransport(app=app)` — mówi httpx żeby wywołał aplikację ASGI bezpośrednio zamiast przez socket sieciowy. Odpowiednik tego co `TestClient` robi wewnętrznie, ale w trybie async.

`base_url="http://test"` — wymagany przez httpx jako parametr obowiązkowy. httpx buduje pełny URL przez złączenie `base_url` z ścieżką podaną w metodzie:

```python
client.post("/v1/users")
# httpx łączy: "http://test" + "/v1/users" → "http://test/v1/users"
```

Wartość `"http://test"` jest konwencją — `test` to nieistniejąca domena, celowo fikcyjna. Gdy `ASGITransport` jest używany, httpx nigdy nie próbuje nawiązać prawdziwego połączenia sieciowego — `base_url` jest potrzebny tylko do zbudowania poprawnego obiektu `Request` (httpx wymaga pełnego URL wewnętrznie). Domena nie ma znaczenia, ale musi być syntaktycznie poprawnym URL z schematem (`http://` lub `https://`).

Inne spotykane wartości — wszystkie równoważne:

```python
base_url="http://test"          # najczęstsza konwencja
base_url="http://testserver"    # używana przez Starlette TestClient wewnętrznie
base_url="http://localhost"     # też działa
```

### NullPool — problem connection pool między testami

pytest-asyncio domyślnie tworzy osobny event loop dla każdego testu. SQLAlchemy engine
jest singletonem na poziomie modułu — jego connection pool reużywa połączeń asyncpg
między testami.

Problem: połączenie asyncpg stworzone w event loop testu A trafia do pool. Test B
dostaje to samo połączenie — ale jego wewnętrzny `_protocol` jest przywiązany do loop A.
Gdy test B próbuje stworzyć SAVEPOINT (bo sesja była już wcześniej użyta),
asyncpg tworzy Future w loop A — test B działa w loop B:

```
E   RuntimeError: Task got Future attached to a different loop
```

Fix: wyłączyć pooling dla testów przez `NullPool`. Każde `engine.connect()` tworzy
wtedy świeże połączenie w bieżącym event loop — żadne stare asyncpg `_protocol`
nie przeżywa między testami:

```python
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

test_engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,
)

@pytest.fixture(scope="function")
async def db_session():
    async with test_engine.connect() as connection:
        await connection.begin()
        async_session = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as session:
            yield session
        await connection.rollback()
```

`NullPool` — SQLAlchemy nie trzyma połączeń w pool. Każde `connect()` otwiera nowe
połączenie i zamyka je po użyciu. Brak reużycia = brak konfliktu event loop między testami.

Kiedy SAVEPOINT jest tworzony automatycznie: gdy sesja jest powiązana z zewnętrzną
transakcją (`connection.begin()`) i była już wcześniej użyta w tym samym teście
(np. przez poprzedni request lub bezpośredni `flush()`). SQLAlchemy tworzy wtedy
SAVEPOINT zamiast nowej transakcji. Z `NullPool` każde połączenie jest świeże —
asyncpg `_protocol` jest zawsze przywiązany do bieżącego event loop.

### Co NullPool faktycznie rozwiązuje

`NullPool` eliminuje błąd "different loop" — po naprawie pojawia się właściwy błąd:

```
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint "uq_users_email"
```

To jest oczekiwane zachowanie. `NullPool` nie ukrywa błędów — odsłania je. Zamiast
mylącej awarii na poziomie asyncpg dostajesz konkretny `IntegrityError` który możesz
obsłużyć w routerze.

### Pułapka — import IntegrityError

`IntegrityError` istnieje w dwóch miejscach — SQLAlchemy i stdlib `sqlite3`:

```python
from sqlite3 import IntegrityError          # ← błąd — nigdy nie zostanie rzucony przez SQLAlchemy
from sqlalchemy.exc import IntegrityError   # ← poprawnie
```

Gdy zaimportujesz z `sqlite3`, `except IntegrityError` nigdy nie złapie wyjątku
z SQLAlchemy — propaguje dalej i FastAPI zwraca 500 zamiast 409.
Błąd jest trudny do zauważenia bo kod wygląda poprawnie — różni się tylko ścieżką importu.

### Sync fixture zależna od async — problem event loop

`client_httpx` jako sync fixture zależna od async `db_session` może powodować
subtelny błąd przy testach z wieloma requestami:

```python
# Problematyczne — sync fixture
@pytest.fixture(scope="function")
def client_httpx(db_session):
    ...
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
```

pytest-asyncio może uruchomić async fixture (`db_session`) w innym kontekście event loop
niż test. Asyncpg connection tworzy się w jednym loop, test wykonuje się w drugim.

Pierwszy request działa — SQLAlchemy nie tworzy SAVEPOINT (świeża sesja).
Drugi request failuje — SQLAlchemy tworzy SAVEPOINT dla drugiego `flush()`, asyncpg
wykrywa niezgodność loop:

```
E   RuntimeError: Task got Future attached to a different loop
```

Fix: zadeklarować `client_httpx` jako **async** fixture:

```python
# Poprawnie — async fixture
@pytest.fixture(scope="function")
async def client_httpx(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()
```

`async def` gwarantuje że fixture i test działają w dokładnie tym samym event loop —
asyncpg connection jest dostępne bez konfliktu loop przy każdym kolejnym requeście.

Test musi być `async` z `await`:

```python
@pytest.mark.integration
async def test_create_user(client):
    response = await client.post("/v1/users/", json={
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": "jan@example.com",
    })
    assert response.status_code == 201
```

### Kiedy zostać przy TestClient

`TestClient` jest wystarczający gdy testy nie używają async fixtures współdzielących zasoby z aplikacją — np. testy endpointów które nie dotykają bazy (health check, walidacja plików). Dla testów z `db_session` i `override_get_db` — zawsze `AsyncClient`.

### 307 Temporary Redirect — pułapka przy AsyncClient

FastAPI przekierowuje gdy URL w teście nie zgadza się z trailing slashem endpointu:

```
POST /v1/users      →  307 →  POST /v1/users/   (endpoint ma "/")
POST /v1/users/     →  307 →  POST /v1/users    (endpoint ma "")
```

`AsyncClient` domyślnie nie podąża za przekierowaniami — dostajesz 307 zamiast oczekiwanego statusu. `TestClient` podąża automatycznie, więc ten problem nie ujawnia się przy synchronicznych testach.

Rozwiązanie: dopasuj URL w teście do ścieżki endpointu. Patrz sekcja `"" vs "/"` w `users_table_plan.md`.

---

## Co mockujemy w integration testach

Znacznie mniej niż w unit testach. Zasada: **mockujesz to czego nie możesz kontrolować
lub co jest zbyt kosztowne**.

**Zewnętrzne API** — jeśli kod woła OpenAI, płatności, email — mockujesz tak samo jak
w unit testach. Nie chcesz wysyłać prawdziwych emaili ani płacić za tokeny podczas testów.

**System plików** — wybór:
- użyć prawdziwego tymczasowego katalogu (`tmp_path` w pytest) — preferowane
- mockować `Path.write_bytes` — możliwe, ale kruche

W `elredactor` endpoint zapisuje plik do `UPLOAD_DIR`. W integration testach podmienisz
`UPLOAD_DIR` na tymczasowy katalog tworzony przez pytest — nie mockujesz,
po prostu używasz innej ścieżki.

**Czas i UUID** — zależy od potrzeby. Jeśli testujesz że `document_id` jest poprawnym
UUID, nie musisz mockować. Jeśli testujesz że data utworzenia jest "teraz" — musisz
mockować `datetime.now()`.

---

## Baza danych w integration testach

### Podejście 1 — Osobna baza testowa

Tworzysz drugą bazę PostgreSQL (np. `elredactor_test`) obok deweloperskiej.
W konfiguracji testów podajesz inne `POSTGRES_DB`.

**Zalety:** prosta koncepcja, działa lokalnie bez Dockera
**Wady:** musisz ręcznie zadbać o migracje, resetowanie stanu, możliwe konflikty
przy równoległych testach

### Podejście 2 — Docker Compose w CI/CD

W pipeline CI startujesz serwis PostgreSQL jako kontener:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_DB: elredactor_test
```

Testy chodzą przeciwko tej bazie, kontener niszczony po zakończeniu pipeline.

**Zalety:** identyczne środowisko co produkcja, czyste przy każdym uruchomieniu CI
**Wady:** wolniejszy start pipeline, wymaga Dockera lokalnie

### Podejście 3 — SQLite in-memory

Zamiast PostgreSQL używasz lekkiej bazy SQLite żyjącej tylko w pamięci RAM.

```python
engine = create_engine("sqlite:///:memory:")
```

**Zalety:** błyskawiczny start, zero konfiguracji, działa wszędzie
**Wady:** SQLite i PostgreSQL różnią się — typy danych (`JSONB`, `UUID`, `ARRAY`),
zachowanie transakcji, współbieżność. Test może przejść na SQLite a wywalić się
na PostgreSQL.

**Rekomendacja dla `elredactor`:** podejście 2 (Docker) w CI + podejście 1
(osobna baza) lokalnie. Projekt ma już `docker-compose.dev.yml` — to naturalna podstawa.

---

## Izolacja między testami

Kluczowy problem: jeden test nie może zostawiać danych które wpłyną na następny.
Testy zależne od kolejności uruchomienia to poważny problem.

### Podejście 1 — Rollback transakcji

Każdy test działa wewnątrz transakcji która jest cofana po zakończeniu.

```
Test startuje → otwiera transakcję → wykonuje operacje → ROLLBACK → baza czysta
```

**Zalety:** bardzo szybkie — rollback jest tani
**Wady:** nie testuje zachowania przy faktycznym commicie. Jeśli kod ma logikę
`ON COMMIT` lub używa wielu transakcji — rollback może nie wyczyścić wszystkiego.

### Podejście 2 — Truncate tabel

Przed każdym testem czyścisz wszystkie tabele:

```sql
TRUNCATE TABLE documents, users RESTART IDENTITY CASCADE;
```

**Zalety:** pewne i przewidywalne, testuje prawdziwe commity
**Wady:** wolniejsze niż rollback, musisz znać listę tabel

### Podejście 3 — Osobna baza na każdy test

Tworzysz i niszczysz całą bazę dla każdego testu. Maksymalna izolacja.

**Zalety:** absolutna pewność izolacji
**Wady:** bardzo wolne, praktycznie niestosowane

**Rekomendacja dla `elredactor`:** rollback transakcji jako domyślne podejście,
z możliwością przełączenia na truncate dla testów które tego wymagają.
`db/` jest obecnie puste — strategię wdrożymy gdy pojawią się modele.

---

## IntegrityError i SAVEPOINT w testach integracyjnych

### Problem — transakcja w stanie ABORTED

Gdy `flush()` narusza UNIQUE constraint, PostgreSQL rzuca `UniqueViolation`.
SQLAlchemy przekształca to w `IntegrityError`. Jeśli router tego nie obsłuży,
wyjątek propaguje w górę — ale połączenie zostaje w stanie ABORTED:

```
BEGIN
  INSERT INTO users ...   ← flush() → UniqueViolation
  -- PostgreSQL: transakcja ABORTED
  SELECT ...              ← ERROR: current transaction is aborted
  INSERT ...              ← ERROR: current transaction is aborted
ROLLBACK                  ← jedyne co można zrobić
```

Po naruszeniu constrainta PostgreSQL blokuje wszystkie kolejne operacje
na tym połączeniu aż do `ROLLBACK`. Dlatego drugi request w tym samym teście
failuje — `db_session` fixture trzyma jedno połączenie przez cały test.

Objaw w testach: `RuntimeError: Task got Future attached to a different loop` —
myląca nazwa, prawdziwa przyczyna to zepsute połączenie po nieobsłużonym błędzie transakcji.

### Rozwiązanie — SAVEPOINT

SAVEPOINT to punkt przywrócenia wewnątrz transakcji — mini-transakcja zagnieżdżona
w większej. `ROLLBACK TO SAVEPOINT` cofa tylko zagnieżdżoną część, zewnętrzna
transakcja pozostaje aktywna:

```
BEGIN
  INSERT first_user          ← OK
  SAVEPOINT sp1
    INSERT duplicate_user    ← UniqueViolation
  ROLLBACK TO SAVEPOINT sp1  ← cofasz tylko ten fragment
  -- transakcja żyje dalej, nie jest ABORTED
ROLLBACK                     ← rollback całości (fixture cleanup)
```

W SQLAlchemy SAVEPOINT tworzy `begin_nested()`:

```python
async def create_user(db_session: AsyncSession, data: UserCreate) -> User:
    user = User(**data.model_dump())
    async with db_session.begin_nested():  # otwiera SAVEPOINT
        db_session.add(user)
        await db_session.flush()
    await db_session.refresh(user)
    return user
```

Jeśli `flush()` rzuci `IntegrityError` — SQLAlchemy automatycznie robi
`ROLLBACK TO SAVEPOINT`. Router łapie wyjątek i zwraca 409.
Zewnętrzna transakcja pozostaje aktywna — test może kontynuować.

### Router musi obsługiwać IntegrityError

Bez obsługi w routerze FastAPI zwróci 500 zamiast 409:

```python
from sqlalchemy.exc import IntegrityError

@router.post("")
async def create_new_user(user_create: UserCreate, session: AsyncSession = Depends(get_db)):
    try:
        user = await create_user(db_session=session, data=user_create)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")
    return UserResponse.model_validate(user)
```

### Dlaczego `begin_nested()` a nie obsługa tylko w routerze

Sam `try/except IntegrityError` w routerze bez SAVEPOINT w crud nie wystarczy —
po `IntegrityError` transakcja jest ABORTED i router nie może już nic zwrócić
przez to samo połączenie. SAVEPOINT izoluje błąd na poziomie bazy danych,
zanim wyjątek dotrze do routera.

---

## Konfiguracja pytest

### `pyproject.toml` vs `pytest.ini` — które wybrać?

Dwa miejsca gdzie można skonfigurować pytest:

| | `pyproject.toml` | `pytest.ini` |
|--|-----------------|--------------|
| Podejście | Nowoczesne — jeden plik dla całego projektu | Starsze — osobny plik tylko dla pytest |
| Inne narzędzia | ruff, mypy, mutmut, coverage w tym samym pliku | Każde narzędzie ma swój plik |
| Obsługa | Wszystkie nowoczesne wersje pytest | Zawsze działało |

**Dla `elredactor`:** używamy `pyproject.toml` — projekt już ma tam konfigurację
ruff i mypy. Jeden plik dla wszystkiego, spójny styl.

---

### Konfiguracja `[tool.pytest.ini_options]` dla `elredactor`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --cov=app --cov-report=term-missing"
asyncio_mode = "auto"
markers = [
    "unit: unit tests — no external services",
    "integration: integration tests — requires PostgreSQL and Qdrant",
    "e2e: end-to-end tests — requires full stack and Playwright",
]
```

### Omówienie każdej opcji

**`testpaths = ["tests"]`**

Bez tego pytest skanuje cały projekt — wchodzi w `app/`, `docs/`, `.github/` itd.
Z tym ustawieniem szuka testów tylko w `tests/`. Można uruchomić `pytest` bez
podawania ścieżki.

**`addopts = "-v --tb=short --cov=app --cov-report=term-missing"`**

Domyślne flagi doklejane do każdego uruchomienia:
- `-v` — verbose, pokazuje nazwę każdego testu
- `--tb=short` — skrócony traceback przy błędzie (to samo co CI)
- `--cov=app` — mierzy pokrycie kodu w folderze `app/`
- `--cov-report=term-missing` — w terminalu pokazuje które linie nie są pokryte

**`asyncio_mode = "auto"`**

Projekt używa async stacku (`asyncpg`, SQLAlchemy async, FastAPI async endpoints).
Bez tego każda async funkcja testowa wymaga dekoratora `@pytest.mark.asyncio`.
Z `auto` — pytest-asyncio wykrywa async testy automatycznie. Zero boilerplate'u.

**`markers`**

Definiuje własne markery odpowiadające strukturze katalogów. Bez definicji pytest
wyświetla `PytestUnknownMarkWarning` przy ich użyciu. Z definicją można uruchamiać
podzbiory testów:

```bash
pytest -m unit             # tylko unit testy
pytest -m integration      # tylko integration testy
pytest -m "not e2e"        # wszystko poza e2e
```

---

### Jak powinien wyglądać `pytest.ini` (dla porównania)

Jeśli ktoś używa osobnego pliku zamiast `pyproject.toml`:

```ini
[pytest]
testpaths = tests
addopts = -v --tb=short --cov=app --cov-report=term-missing
asyncio_mode = auto
markers =
    unit: unit tests — no external services
    integration: integration tests — requires PostgreSQL and Qdrant
    e2e: end-to-end tests — requires full stack and Playwright
```

Składnia identyczna w treści, różna w formacie. Dla `elredactor` tego pliku
**nie tworzymy** — całość idzie do `pyproject.toml`.

---

## Fixtures dla testów uploadów

### `sample_pdf` — minimalny PDF w pamięci

```python
@pytest.fixture
def sample_pdf() -> bytes:
    return b"%PDF-1.4 1 0 obj<</Type/Catalog>>endobj"
```

Co oznacza ta treść:

`%PDF-1.4` — nagłówek z wersją formatu. Parsery PDF sprawdzają czy plik zaczyna się od `%PDF-`.

`1 0 obj<</Type/Catalog>>endobj` — jeden obiekt PDF:
- `1` — numer obiektu (ID)
- `0` — numer generacji (0 = obiekt nigdy nie był usuwany i tworzony ponownie)
- `obj` — słowo kluczowe otwierające obiekt
- `<< ... >>` — słownik PDF (odpowiednik JSON object; `<<` otwiera, `>>` zamyka)
- `/Type/Catalog` — klucz `/Type` z wartością `/Catalog`; `Catalog` to korzeń drzewa dokumentu PDF, punkt wejścia dla każdego readera
- `endobj` — słowo kluczowe zamykające obiekt

Pełny plik PDF wymagałby jeszcze `xref` (tabela gdzie w pliku leży każdy obiekt) i `trailer` (wskazuje na Catalog). Żaden reader nie otworzy tego pliku — ale do testu uploadera który sprawdza tylko `content_type` i rozmiar wystarczy.

Można też użyć `b"fake pdf content"` — `UploadValidator` nie parsuje zawartości. Magic bytes to kosmetyka, nie wymóg.

### `tmp_path` vs własna fixture `tmp_upload_dir`

`tmp_path` to wbudowana fixture pytest — tworzy tymczasowy katalog unikalny dla każdego testu i usuwa go automatycznie po zakończeniu. Ma `scope="function"` — każdy test dostaje świeży katalog.

```python
def test_upload_pdf(test_client, sample_pdf, tmp_path):
    with patch("app.api.v1.routers.documents.UPLOAD_DIR", tmp_path):
        response = test_client.post(
            "/v1/documents/upload",
            files={"file": ("test.pdf", sample_pdf, "application/pdf")},
        )
    assert response.status_code == 200
    saved = tmp_path / f"{response.json()['document_id']}.pdf"
    assert saved.exists()
```

Dodatkowa fixture `tmp_upload_dir` nie ma sensu gdy jest tylko aliasem:

```python
# Nadmiarowe — nic nie dodaje do tmp_path
@pytest.fixture
def tmp_upload_dir(tmp_path):
    return tmp_path
```

`tmp_upload_dir` miałoby sens gdyby fixture robiła coś więcej — tworzyła podkatalog,
ustawiała uprawnienia, albo była parametryzowana różnymi ścieżkami. Gdy nic nie robi
poza zwróceniem `tmp_path` — używaj `tmp_path` bezpośrednio.

---

## `dependency_overrides` — podmiana dependency w testach

### Problem

Gdy router wymaga autoryzacji przez `Depends(get_current_credential)`, każdy test
który nie wysyła nagłówków `X-Api-Key`/`X-Api-Secret` dostanie `422` — FastAPI
waliduje wymagane nagłówki zanim dotrze do logiki endpointu.

Testy `users` i `documents` testują logikę biznesową, nie autoryzację. Autoryzacja
testowana jest osobno. Dlatego dependency weryfikującą credential podmieniana jest na fake.

### Mechanizm

`app.dependency_overrides` to słownik — klucz to oryginalna funkcja dependency,
wartość to funkcja zastępcza:

```python
app.dependency_overrides[get_current_credential] = override_get_current_credential
```

FastAPI przy każdym requeście sprawdza czy dependency ma override — jeśli tak,
wywołuje zastępczą zamiast oryginalnej. Override jest aktywny dopóki nie zostanie
usunięty (`app.dependency_overrides.clear()`).

### Implementacja w conftest

Override jako funkcja modułu (nie fixture) — współdzielona przez oba klienty:

```python
async def override_get_current_credential() -> ApiCredential:
    return ApiCredential(
        id=uuid.uuid4(), user_id=uuid.uuid4(), key="test-key", secret_hash="x"
    )

@pytest.fixture(scope="function")
def client_fastapi(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_credential] = override_get_current_credential
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def client_httpx(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_credential] = override_get_current_credential
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()
```

`app.dependency_overrides.clear()` po `yield` — czyści wszystkie overrides po każdym teście.
Bez tego overrides wyciekałyby między testami.

### Dwa klienty — kiedy który

| Fixture | Typ | Używany w |
|---------|-----|-----------|
| `client_fastapi` | `TestClient` (sync) | testy documents — sync `def test_*` |
| `client_httpx` | `AsyncClient` (async) | testy users — async `async def test_*` z `db_session` |

`TestClient` opakowuje aplikację ASGI w synchroniczny interfejs — działa w sync testach.
`AsyncClient` wymagany gdy test jest `async` i współdzieli event loop z `db_session`.

### Dlaczego `override_get_current_credential` nie jest fixture

Jest zwykłą funkcją modułu zamiast fixture dlatego, że nie potrzebuje żadnych
zależności od pytest (nie przyjmuje innych fixtures, nie ma scope). Fixture byłoby
nadmiarowe — wystarczy funkcja której referencję przekazujesz do `dependency_overrides`.

Gdyby fake credential potrzebował danych z bazy albo z innej fixture — wtedy
warto by go zrobić fixture i wstrzyknąć do `client_fastapi`/`client_httpx`.

## Lintowanie, formatowanie i typy — ruff, mypy, pre-commit

**Ruff** robi lintowanie (`ruff check`) i formatowanie (`ruff format`). **Mypy** tylko sprawdza typy
i nie formatuje kodu. Konfigurację obu narzędzi trzymamy w `pyproject.toml`
(`[tool.ruff]`, `[tool.mypy]`), a sprawdzamy `src` i `tests`.

### Kiedy uruchamiać narzędzia — opcje

| Opcja | Kiedy działa | Zalety | Wady |
|---|---|---|---|
| **Ręcznie** | Gdy wpiszesz `uv run ruff check`, `uv run ruff format`, `uv run mypy src tests` | Zero konfiguracji | Łatwo zapomnieć |
| **Skrypty / taski** | Jedno polecenie, np. `uv run poe check` albo `Makefile` | Jedna komenda zamiast trzech | Nadal uruchamiasz ręcznie |
| **Git hook (`pre-commit`)** | Automatycznie przy każdym `git commit` | Złego kodu nie da się zacommitować, konfiguracja wersjonowana w repo | Trochę konfiguracji, commit trwa dłużej |
| **Ręczny skrypt w `.git/hooks`** | Przy commicie | Bez dodatkowych zależności | Nie trafia do repo, nie da się współdzielić |
| **CI (np. GitHub Actions)** | Po pushu na serwerze | Nie da się obejść przez `--no-verify` | Feedback dopiero po pushu |
| **Edytor / IDE** | Przy zapisie pliku | Najszybszy feedback | Zależy od ustawień każdego developera |

Dobre połączenie: hook lokalnie (szybki feedback) plus CI jako bezpiecznik.

### Czym jest `pre-commit`

**`pre-commit`** to narzędzie napisane w Pythonie (pakiet z PyPI, instalowany jak `pytest` czy
`ruff`), które zarządza hookami gita. Samo nie sprawdza kodu — uruchamia inne narzędzia (tu ruff
i mypy) w odpowiednim momencie.

**Framework, nie biblioteka:** to ono steruje przebiegiem (czyta konfigurację, wybiera pliki,
uruchamia hooki, decyduje o przerwaniu commita), a Ty podajesz tylko listę narzędzi.

Git pozwala podpiąć dowolny skrypt pod commit (`.git/hooks/pre-commit`), ale niczego więcej nie
daje. Pisząc taki skrypt ręcznie, trzeba samemu obsłużyć listę zmienionych plików, kolejność,
kody wyjścia i współdzielenie z zespołem (`.git/hooks` nie trafia do repo). `pre-commit` robi to
za nas:

- czyta konfigurację z `.pre-commit-config.yaml` i uruchamia hooki po kolei,
- przekazuje im zmienione pliki i filtruje je po typie (`types: [python]`) lub ścieżce (`files`),
- przerywa commit, jeśli którykolwiek hook zwróci błąd albo zmodyfikuje pliki,
- zarządza środowiskami zewnętrznych hooków (przy hookach `local` nie jest to potrzebne).

#### `.pre-commit-config.yaml` a `.git/hooks`

- **`.pre-commit-config.yaml`** to tylko konfiguracja: lista poleceń, plików i kolejność. Leży
  w katalogu głównym projektu i jest zwykłym plikiem w repo (commitujemy go).
- **`.git/hooks/pre-commit`** to mały skrypt-wrapper, który zapisuje komenda
  `pre-commit install`. Nie zawiera reguł, tylko woła `pre-commit run`, a ten czyta YAML.

Przebieg: `git commit` → uruchamia `.git/hooks/pre-commit` → wywołuje `pre-commit run` → czyta
`.pre-commit-config.yaml` → uruchamia hooki. Zmiany w YAML działają od razu, bez ponownej
instalacji.

**Konsekwencja:** `.git/hooks` nie jest wersjonowane, więc po sklonowaniu repo na nowej maszynie
trzeba raz uruchomić `uv run pre-commit install`. Sam YAML przyjedzie z repo.

#### Najczęściej używane komendy

| Komenda | Co robi |
|---|---|
| `pre-commit install` | Podpina hook pod git (raz na klon repo) |
| `pre-commit run --all-files` | Odpala wszystkie hooki na całym projekcie, nie tylko na zmienionych plikach |
| `pre-commit run <id>` | Odpala jeden hook po jego `id`, np. `ruff-check` |
| `pre-commit uninstall` | Usuwa hook z gita |

### Git hook z `pre-commit` — jak to zrealizować

1. W `pyproject.toml`: dodać `pre-commit` do grupy dev oraz sekcje `[tool.ruff]`,
   `[tool.ruff.lint]` i `[tool.mypy]`.
2. Utworzyć `.pre-commit-config.yaml` z trzema hookami w tej kolejności:
   - `ruff check --fix` (lintowanie z autofixem),
   - `ruff format` (formatowanie),
   - `mypy` (typy; ścieżki bierze z `files` w `[tool.mypy]`).
3. Zainstalować hook w gicie: `uv run pre-commit install`.
4. Dodać pusty `tests/__init__.py` — mypy odmawia pracy na katalogu bez plików `.py`.
5. Sprawdzić całość: `uv run pre-commit run --all-files`.

Hooki są typu `local` z `uv run`, żeby używać wersji z `uv.lock`, a mypy widział zainstalowane
zależności projektu (gotowy mirror mypy działa w izolowanym środowisku).

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]
        files: ^(src|tests)/
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
        files: ^(src|tests)/
      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        types: [python]
        pass_filenames: false
```

`pass_filenames: false` przy mypy: nie przekazujemy zmienionych plików, więc mypy sprawdza cały
projekt (`files = ["src", "tests"]` z `pyproject.toml`). Ma to znaczenie, bo błąd typów może
wynikać ze zmiany w innym pliku. Kolejność hooków też jest ważna: `ruff check --fix` przed
`ruff format` (autofix może zmienić formatowanie), a mypy na końcu, bo działa na gotowym kodzie.

**Autofix:** `ruff check --fix` i `ruff format` modyfikują pliki. Gdy coś zmienią, commit jest
przerwany — robisz `git add` i commit jeszcze raz. To normalne zachowanie pre-commit.
Hook można pominąć przez `git commit --no-verify`.

Testów (`pytest`) zwykle nie wpina się w hook commita, bo spowalniają pracę — lepiej na
`pre-push` albo do CI.

### Mypy w trybie strict

```toml
[tool.mypy]
strict = true
files = ["src", "tests"]
```

`strict` włącza m.in. wymóg adnotacji we wszystkich funkcjach, zakaz niejawnego `Any` i
sprawdzanie ciał funkcji bez typów. W testach oznacza to `def test_add_stock() -> None:` oraz
adnotacje fixture'ów, np. `def product() -> Product:`.

#### Adnotacje w testach — opcje

Strict wymaga adnotacji **każdego** parametru, nie tylko `-> None`. Dotyczy to też argumentów
z `parametrize` i fixtures wstrzykiwanych do testu. Brak typu daje błąd
`Function is missing a type annotation for one or more parameters [no-untyped-def]`.

**Opcja 1: pełne adnotacje (zalecana)** — typ opisuje dane, a mypy łapie błędy, np. po zmianie
kolejności pól w klasie:

```python
@pytest.mark.parametrize("invalid_product_data", [("Battery", -10.25, 5)])
def test_product_negative_price(invalid_product_data: tuple[str, float, int]) -> None:
    with pytest.raises(ValueError, match="Price cannot be negative"):
        Product(*invalid_product_data)
```

Typ fixture to zwykle po prostu typ zwracany: `def product() -> Product:`, a w teście
`def test_x(product: Product) -> None:`.

**Opcja 2: alias typu** — skraca zapis przy powtarzającym się typie, bez utraty informacji:

```python
ProductData = tuple[str, float, int]

def test_product_negative_price(invalid_product_data: ProductData) -> None: ...
```

**Opcja 3: `Any` dla wybranych parametrów** — spełnia wymóg strict, ale niczego nie sprawdza,
więc to tylko obejście:

```python
from typing import Any

def test_product_negative_price(invalid_product_data: Any) -> None: ...
```

**Opcja 4: luźniejsze reguły tylko dla `tests`** — `src` zostaje w pełnym strict:

```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

Potrzebne są **obie** opcje: `disallow_untyped_defs` obejmuje funkcje bez żadnych adnotacji,
a `disallow_incomplete_defs` te z częściowymi, np. `def test(x) -> None`. Reszta strict
(w tym `check_untyped_defs`) nadal działa — mypy sprawdza ciała testów, ale nieotypowane
parametry traktuje jako `Any`.

| Opcja | Zaleta | Wada |
|---|---|---|
| 1. Pełne adnotacje | Mypy łapie błędy w danych testowych | Trochę pisania |
| 2. Alias typu | Krótszy zapis, pełna informacja | Dodatkowa nazwa do zapamiętania |
| 3. `Any` | Szybko, bez zmiany konfiguracji | Brak kontroli typów dla parametru |
| 4. Override dla `tests.*` | Zero adnotacji w testach | Mypy nie weryfikuje typów parametrów |

#### Typowe błędy mypy w testach

| Komunikat | Przyczyna | Poprawka |
|---|---|---|
| `Function is missing a type annotation for one or more parameters` | Parametr testu (fixture lub z `parametrize`) bez typu | Dodać typ, np. `product: Product` |
| `Function is missing a return type annotation` | Brak `-> None` | Dodać `-> None` |
| `Skipping analyzing "shop.product": module is installed, but missing library stubs or py.typed marker` | Import `from shop.product import ...` zamiast `from src.shop.product import ...` | Importować ze ścieżką od katalogu głównego i trzymać jeden styl w całym projekcie |

Mieszanie `shop.` i `src.shop.` jest ryzykowne: Python wczyta ten sam moduł pod dwiema nazwami,
jako dwie osobne klasy, a mypy potraktuje zainstalowany pakiet jako bibliotekę bez typów.

> Uwaga: plik z fixtures musi nazywać się **`conftest.py`**. Literówka (np. `contest.py`)
> sprawia, że pytest go nie wczyta, a fixtures będą niewidoczne dla testów. Fixture lepiej też
> nie nazywać `test_*` — w pliku z testami pytest wziąłby ją za test.

### Reguły ruff

Reguły są pogrupowane w zestawy oznaczone literami i włączane przez `select`:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "SIM", "C4", "PT"]
```

| Kod | Nazwa | Co sprawdza |
|---|---|---|
| **E, W** | pycodestyle | Styl PEP 8: spacje, wcięcia, zbyt długie linie |
| **F** | pyflakes | Prawdziwe błędy: nieużywane importy i zmienne, niezdefiniowane nazwy |
| **I** | isort | Sortowanie i grupowanie importów |
| **B** | bugbear | Typowe pułapki, np. mutowalny argument domyślny `def f(x=[])` |
| **UP** | pyupgrade | Nowoczesna składnia, np. `list[int]` zamiast `List[int]` |
| **SIM** | simplify | Upraszczanie kodu, np. `if x: return True else: return False` |
| **C4** | comprehensions | Lepsze listy składane zamiast `list(map(...))` |
| **PT** | flake8-pytest-style | Konwencje pytesta: `pytest.raises` z `match=`, nazwy w `parametrize` |

- `PT` jest szczególnie przydatny przy nauce pytesta — wskazuje niezalecany styl, np.
  `pytest.raises(ValueError)` bez `match`.
- Domyślnie ruff włącza tylko `E` (część) i `F`.
- Autofixowalne są m.in. `F` (nieużywane importy), `I`, `UP`, `C4` i część `SIM`. Reguły `B` i `E`
  zwykle tylko zgłaszają problem.
- Na początek bez `D` (docstringi) i `ANN` (adnotacje — to robi już mypy), bo zasypałyby
  błędami.
- Domyślna długość linii w ruff to 88 znaków (jak w black); powyżej ustawione 100.
