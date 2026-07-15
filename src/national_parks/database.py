"""Legacy dump loading and export helpers."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import pandas as pd
import pgdumplib

COPY_COLUMNS_RE = re.compile(r"\((?P<columns>.+)\)")


def load_legacy_dump(dump_path: Path):
    if not dump_path.exists():
        raise FileNotFoundError(f"Legacy dump not found: {dump_path}")
    return pgdumplib.load(dump_path)


def get_table_entry(dump: Any, schema: str, table: str):
    for entry in dump.entries:
        if entry.desc == "TABLE DATA" and entry.namespace == schema and entry.tag == table:
            return entry
    raise ValueError(f"Table data entry not found for {schema}.{table}")


def get_table_columns(dump: Any, schema: str, table: str) -> list[str]:
    entry = get_table_entry(dump, schema, table)
    match = COPY_COLUMNS_RE.search(entry.copy_stmt)
    if not match:
        raise ValueError(f"Unable to parse copy statement for {schema}.{table}")
    return [column.strip() for column in match.group("columns").split(",")]


def table_to_dataframe(dump: Any, schema: str, table: str) -> pd.DataFrame:
    columns = get_table_columns(dump, schema, table)
    rows = list(dump.table_data(schema, table))
    return pd.DataFrame(rows, columns=columns)


def export_table_to_csv(dump_path: Path, schema: str, table: str, output_path: Path) -> Path:
    dump = load_legacy_dump(dump_path)
    frame = table_to_dataframe(dump, schema, table)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)
    return output_path


def legacy_table_definitions(dump: Any) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for entry in dump.entries:
        if entry.desc == "TABLE" and entry.namespace == "public":
            definitions[entry.tag] = entry.defn
    return definitions

