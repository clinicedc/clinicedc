from datetime import date, datetime

from ..reference_range_collection import ReferenceRangeCollection
from .get_normal_data_or_raise import get_normal_data_or_raise


def in_bounds_or_raise(
    reference_range_collection: ReferenceRangeCollection,
    name: str,
    value: int | float,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
) -> bool:
    obj = get_normal_data_or_raise(
        reference_range_collection=reference_range_collection,
        label=name,
        units=units,
        gender=gender,
        dob=dob,
        report_datetime=report_datetime,
        age_units=age_units,
    )
    return obj.value_in_normal_range_or_raise(
        value=value, dob=dob, report_datetime=report_datetime, age_units=age_units
    )
