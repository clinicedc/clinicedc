from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from edc_utils import age as age_as_rdelta

from ...convert_units import ConversionNotHandled, convert_units
from ...exceptions import NotEvaluated
from ..normal_data import NormalData


def get_normal_data_or_raise(
    label: str = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
):
    obj = None

    age_units = age_units or "years"
    rdelta = age_as_rdelta(dob, report_datetime)
    age = getattr(rdelta, age_units)

    # TODO: need to consider age
    # if qs := NormalData.objects.filter(label=label, units=units, gender=gender):
    #     for obj in qs:
    try:
        obj = NormalData.objects.get(
            label=label, units=units, gender=gender, age_lower=age, age_units=age_units
        )
    except ObjectDoesNotExist:
        for obj_existing in NormalData.objects.filter(label=label, gender=gender).annotate(
            unit=Count("units")
        ):
            opts = {
                k: v
                for k, v in obj_existing.__dict__.items()
                if not k.startswith("_") and k not in ["id", "unit"]
            }
            try:
                opts["lower"] = convert_units(
                    obj_existing.lower,
                    units_from=obj_existing.units,
                    units_to=units,
                    places=2,
                )
            except ConversionNotHandled:
                continue
            try:
                opts["upper"] = convert_units(
                    obj_existing.upper,
                    units_from=obj_existing.units,
                    units_to=units,
                    places=2,
                )
            except ConversionNotHandled:
                continue
            opts["units"] = units
            obj = NormalData.objects.create(**opts)
            break
        if not obj:
            raise NotEvaluated(
                f"Value not evaluated. "
                f"Normal reference range not found for {label}. "
                f"Using units={units}, gender={gender}. "
            )
    return obj
