from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd


def to_datetime(value: Any) -> datetime | None:
    if value is None or pd.isna(value):
        return None
    return value


def to_decimal(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
