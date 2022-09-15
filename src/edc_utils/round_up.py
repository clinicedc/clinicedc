from __future__ import annotations

import decimal
import math
from decimal import Decimal


def round_up(value: Decimal, places: Decimal | None = None):
    places = places or Decimal("1.0000")
    if value > Decimal("0.0000000000"):
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    else:
        decimal.getcontext().rounding = decimal.ROUND_HALF_DOWN
    return value.quantize(places)


def round_half_up(n, places=0):
    multiplier = 10**places
    return math.floor(n * multiplier + 0.5) / multiplier


def round_half_away_from_zero(n: float | Decimal, places: int | None = None):
    if type(n) == Decimal:
        places = Decimal("1" if not places else f"1.{str(0) * places}")
        return round_up(n, places=places)
    rounded_abs = round_half_up(abs(n), places)
    return math.copysign(rounded_abs, n)
