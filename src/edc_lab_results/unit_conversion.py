from __future__ import annotations

from decimal import Decimal, InvalidOperation

from clinicedc_utils.convert_units import convert_units
from clinicedc_utils.exceptions import ConversionNotHandled

from edc_reportable.models import NormalData

UNIT_ALIASES: dict[str, str] = {
    "U/L": "IU/L",
    "K/uL": "10^9/L",
    "k/uL": "10^9/L",
    "10*3/uL": "10^3/L",
    "10*9/L": "10^9/L",
    "fL": "fL/cell",
    "pg": "pg/cell",
    "µmol/L": "umol/L",
    "μmol/L": "umol/L",
}


def normalize_units(units: str) -> str:
    return UNIT_ALIASES.get(units, units)


def _find_target_units(utest_id: str, source_units: str) -> str | None:
    """Find a NormalData unit to convert to.

    If the source units already match a formula, return None
    (no conversion needed). Otherwise return the first available
    unit for this utest_id.
    """
    available = list(
        NormalData.objects.filter(label=utest_id)
        .values_list("units", flat=True)
        .distinct()
    )
    if not available:
        return None
    if source_units in available:
        return None
    return available[0]


def attempt_conversion(
    utest_id: str,
    value: Decimal | None,
    units: str,
) -> tuple[Decimal | None, str]:
    """Attempt to convert a result value to units recognized
    by edc_reportable.

    Returns (converted_value, converted_units).
    Returns (None, "") if no conversion is needed or possible.
    """
    if not utest_id or value is None or not units:
        return None, ""

    normalized = normalize_units(units)
    target = _find_target_units(utest_id, normalized)
    if target is None:
        return None, ""

    try:
        converted = convert_units(
            label=utest_id,
            value=float(value),
            units_from=normalized,
            units_to=target,
        )
    except (ConversionNotHandled, ValueError, TypeError):
        return None, ""

    try:
        return Decimal(str(converted)), target
    except (InvalidOperation, ValueError):
        return None, ""
