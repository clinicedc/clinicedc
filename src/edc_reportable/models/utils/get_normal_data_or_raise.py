from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from django.contrib.sites.models import Site
from edc_utils import age

from ...convert_units import ConversionNotHandled, convert_units
from ...exceptions import NotEvaluated
from ..normal_data import NormalData

if TYPE_CHECKING:
    from ..reference_range_collection import ReferenceRangeCollection


def get_normal_data_or_raise(
    reference_range_collection: ReferenceRangeCollection,
    label: str = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
    site: Site | None = None,
) -> NormalData:
    obj = None
    age_rdelta = age(dob, report_datetime)
    normal_data_objs = get_normal_data_instances(
        reference_range_collection, label, units, gender, dob, report_datetime, age_units
    )
    if normal_data_objs:
        objs_filtered_by_units = [obj for obj in normal_data_objs if obj.units == units]
        if len(objs_filtered_by_units) == 1:
            obj = objs_filtered_by_units[0]
        elif len(objs_filtered_by_units) > 1:
            # multiple hits for given criteria - ambiguous
            raise NotEvaluated(
                f"Value not evaluated. "
                f"Multiple normal references found for `{label}`. "
                f"Using units={units}, gender={gender}, age={getattr(age_rdelta, age_units)}. "
            )
        elif len(objs_filtered_by_units) == 0:
            # see if we can convert for an existing reference
            # and create the missing reference
            for obj_existing in normal_data_objs:
                try:
                    obj = create_obj_for_new_units_or_raise(obj_existing, units)
                except ConversionNotHandled:
                    continue
                break
    if not obj:
        raise NotEvaluated(
            f"Value not evaluated. "
            f"Normal reference range not found for `{label}`. "
            f"Using units={units}, gender={gender}, age={getattr(age_rdelta, age_units)}. "
        )
    return obj


def get_normal_data_instances(
    reference_range_collection: ReferenceRangeCollection,
    label: str,
    units: str,
    gender: str,
    dob: date,
    report_datetime: datetime,
    age_units: str | None = None,
) -> list[NormalData]:
    normal_data_objs = []
    if age_units not in ["days", "months", "years"]:
        raise ValueError(
            f'Invalid age units. Expected one of {["days", "months", "years"]}. '
            f"Got {age_units}"
        )

    qs = NormalData.objects.filter(
        reference_range_collection=reference_range_collection,
        label=label,
        gender=gender,
        # site__
    )
    # keep those instances that match the age requirement
    for obj in qs:
        if obj.age_in_bounds_or_raise(
            dob=dob, report_datetime=report_datetime, age_units=age_units
        ):
            normal_data_objs.append(obj)
    return normal_data_objs


def create_obj_for_new_units_or_raise(obj, units):
    opts = {
        k: v
        for k, v in obj.__dict__.items()
        if not k.startswith("_") and k not in ["id", "unit"]
    }
    opts["lower"] = convert_units(
        obj.lower,
        units_from=obj.units,
        units_to=units,
        places=2,
    )
    opts["upper"] = convert_units(
        obj.upper,
        units_from=obj.units,
        units_to=units,
        places=2,
    )
    del opts["description"]
    del opts["phrase"]
    opts["units"] = units
    return NormalData.objects.create(**opts)
