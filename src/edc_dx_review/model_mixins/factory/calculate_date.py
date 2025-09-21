from __future__ import annotations

from datetime import date

from django.db import models
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_model import duration_to_date


def calculate_date(
    instance: models.Model, fld_prefix: str, reference_field: str
) -> tuple[date | None, str]:
    """Returns tuple date and YES/NO/NA.

    The date is either the actual date or an estimated date
    based on the ago field value.
    ."""
    calculated_date: date | None = None
    is_estimated: str = NOT_APPLICABLE
    report_datetime = getattr(instance, reference_field)
    rx_date = getattr(instance, f"{fld_prefix}_date")
    rx_ago = getattr(instance, f"{fld_prefix}_ago")
    if rx_ago and not rx_date and report_datetime:
        if rx_ago and not rx_date:
            calculated_date = duration_to_date(rx_ago, report_datetime)
            is_estimated = YES
        elif rx_date:
            calculated_date = rx_date
            is_estimated = NO

        else:
            calculated_date = None
            is_estimated = NOT_APPLICABLE
    return calculated_date, is_estimated


def update_calculated_date(instance: models.Model, fld_prefix: str, reference_field: str):
    """Wrapper for model save method"""
    calculated_date, is_calculated = calculate_date(
        instance=instance, fld_prefix=fld_prefix, reference_field=reference_field
    )
    setattr(instance, f"{fld_prefix}_calculated_date", calculated_date)
    setattr(instance, f"{fld_prefix}_date_is_estimated", is_calculated)
