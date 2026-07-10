from __future__ import annotations

from decimal import Decimal

from .unit_conversion import attempt_conversion, normalize_units

__all__ = ["convert_result"]


def convert_result(
    utestid: str,
    result_value: Decimal | None,
    units: str,
    units_cache: dict,
    unrecognized_units: set[tuple[str, str]],
) -> tuple[Decimal | None, str]:
    """Convert to reportable units; record units with no conversion path."""
    converted_value, converted_units = attempt_conversion(
        utestid, result_value, units, units_cache=units_cache
    )
    if (
        utestid
        and result_value is not None
        and units
        and converted_value is None
        and normalize_units(units) not in units_cache.get(utestid, [])
    ):
        unrecognized_units.add((utestid, units))
    return converted_value, converted_units
