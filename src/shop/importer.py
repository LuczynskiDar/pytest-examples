from pathlib import Path

from src.files.readers import read_csv, read_json
from src.shop.product import Product


class ProductImporter:
    """Load products from CSV and JSON files."""

    CSV_COLUMNS = ("name", "price")

    def load_from_csv(self, path: Path | str) -> list[Product]:
        """Load products from a CSV file with columns: name, price and optional stock."""
        rows = read_csv(path, required_columns=self.CSV_COLUMNS)
        return [self._build_product(index, row) for index, row in enumerate(rows, start=1)]

    def load_from_json(self, path: Path | str) -> list[Product]:
        """Load products from a JSON file containing a list of product objects."""
        data = read_json(path)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of products")
        return [self._build_product(index, item) for index, item in enumerate(data, start=1)]

    @staticmethod
    def _build_product(index: int, row: dict[str, str]) -> Product:
        try:
            return Product(
                name=row["name"],
                price=float(row["price"]),
                stock=int(row.get("stock") or 0),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid product in row {index}: {error}") from error
