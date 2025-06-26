from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from .get_normal_data_or_raise import get_normal_data_or_raise

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection


__all__ = ["in_normal_bounds_or_raise"]


def in_normal_bounds_or_raise(
    reference_range_collection: ReferenceRangeCollection = None,
    label: str = None,
    value: int | float = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
    create_missing_normal: bool | None = None,
) -> bool:
    """Is this used??"""
    obj = get_normal_data_or_raise(
        reference_range_collection=reference_range_collection,
        label=label,
        units=units,
        gender=gender,
        dob=dob,
        report_datetime=report_datetime,
        age_units=age_units,
        create_missing_normal=create_missing_normal,
    )
    return obj.value_in_normal_range_or_raise(
        value=value, dob=dob, report_datetime=report_datetime, age_units=age_units
    )
