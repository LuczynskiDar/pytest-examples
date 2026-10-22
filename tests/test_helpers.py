import csv
import json
from pathlib import Path
from typing import Any

ProductData = tuple[str, float, int]
CustomerData = tuple[str, str]


def read_test_csv(path: str, delimiter: str = ",") -> Any:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter=delimiter)

        return list(reader)


def read_test_dict_csv(path: str, delimiter: str = ",") -> Any:
    with Path(path).open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        return list(reader)


def write_test_csv(path: str, data: list[Any], delimiter: str = ",") -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=delimiter)
        header = data[0]
        writer.writerow(header)
        writer.writerows(data[1:])


def write_test_dict_csv(path: str, data: list[dict[str, Any]], delimiter: str = ",") -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as file:
        header = list(data[0].keys())
        writer = csv.DictWriter(file, fieldnames=header, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)


def read_json(path: str) -> Any:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str, json_data: Any) -> None:
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)
