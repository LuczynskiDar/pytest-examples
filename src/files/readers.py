import csv
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def read_text(path: Path | str) -> str:
    """Return the whole content of a UTF-8 text file."""
    return Path(path).read_text(encoding="utf-8")


def read_lines(path: Path | str) -> list[str]:
    """Return meaningful lines of a text file.

    Lines are stripped, empty lines and lines starting with '#' are skipped.
    """
    lines = (line.strip() for line in read_text(path).splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def read_json(path: Path | str) -> Any:
    """Return parsed JSON content. Raise ValueError if the file is not valid JSON."""
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error.msg}") from error


def read_csv(
    path: Path | str,
    delimiter: str = ",",
    required_columns: Sequence[str] = (),
) -> list[dict[str, str]]:
    """Return CSV rows as dictionaries keyed by the header.

    Raise ValueError if the file has no header or lacks any of the required columns.
    """
    with Path(path).open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file is empty: {path}")
        missing = [column for column in required_columns if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        return list(reader)
