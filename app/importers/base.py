from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import pandas as pd


@dataclass
class ImportResult:
    processed_rows: int
    error_rows: int


def read_excel(content: bytes) -> pd.DataFrame:
    return pd.read_excel(BytesIO(content), engine="openpyxl")


def missing_required_columns(df: pd.DataFrame, required: set[str]) -> list[str]:
    present = {c.strip() for c in df.columns.astype(str)}
    return sorted(required - present)
