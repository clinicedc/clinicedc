from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd


def to_datetime(value: Any) -> datetime | None:
    if value is None or pd.isna(value):
        return None
    return value


def to_str(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value)


def to_decimal(value: Any) -> Decimal | None:
    if value is None or pd.isna(value):
        return None
    if not value and value != 0:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def to_pk(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None
    return value


def to_int(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    if not value and value != 0:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
