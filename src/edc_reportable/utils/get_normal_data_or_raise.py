from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from edc_model_to_dataframe.constants import SYSTEM_COLUMNS
from edc_utils import age as get_age

from ..exceptions import NotEvaluated
from .convert_units import convert_units
from .normal_data_model_cls import normal_data_model_cls

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

    from ..models import NormalData, ReferenceRangeCollection


__all__ = ["get_normal_data_or_raise"]


def get_normal_data_or_raise(
    reference_range_collection: ReferenceRangeCollection = None,
    label: str = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
    site: Site | None = None,
    create_missing_normal: bool | None = None,
) -> NormalData:
    # TODO: ensure all age values are inclusive
    obj = None
    age_rdelta = get_age(dob, report_datetime)
    age = getattr(age_rdelta, age_units)
    try:
        obj = normal_data_model_cls().objects.get(
            (Q(age_lower__lte=age) | Q(age_lower__isnull=True)),
            (Q(age_upper__gte=age) | Q(age_upper__isnull=True)),
            reference_range_collection=reference_range_collection,
            label=label,
            gender=gender,
            units=units,
            age_units=age_units,
        )
    except ObjectDoesNotExist:
        if create_missing_normal:
            opts = dict(
                reference_range_collection=reference_range_collection,
                label=label,
                gender=gender,
                units=units,
                dob=dob,
                report_datetime=report_datetime,
                age_units=age_units,
            )
            obj = create_obj_for_new_units_or_raise(**opts)
        if not obj:
            raise NotEvaluated(
                f"Value not evaluated. "
                f"Normal reference not found for `{label}`. "
                f"Using units={units}, gender={gender}, "
                f"age={getattr(age_rdelta, age_units)}{age_units}. "
                "Perhaps add this to the default normal reference range data or "
                "pass 'create_missing=True' to convert an existing normal reference."
            )
    except MultipleObjectsReturned:
        raise NotEvaluated(
            f"Value not evaluated. "
            f"Multiple normal references found for `{label}`. "
            f"Using units={units}, gender={gender}, age={getattr(age_rdelta, age_units)}. "
        )
    return obj


def create_obj_for_new_units_or_raise(
    reference_range_collection: ReferenceRangeCollection = None,
    label: str = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
) -> NormalData | None:
    opts = {}
    age_rdelta = get_age(dob, report_datetime)
    age = getattr(age_rdelta, age_units)
    # try to find an existing record but with different units
    for obj in (
        normal_data_model_cls()
        .objects.filter(
            (Q(age_lower__lte=age) | Q(age_lower__isnull=True)),
            (Q(age_upper__gte=age) | Q(age_upper__isnull=True)),
            reference_range_collection=reference_range_collection,
            label=label,
            gender=gender,
            age_units=age_units,
        )
        .exclude(units=units)
    ):
        # print(f"Creating normal data: {label} {gender} -- {obj.units}->{units}")
        opts = {
            k: v
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
            and k
            not in [
                "id",
                "units",
                "description",
                "phrase",
                "lower",
                "upper",
                *SYSTEM_COLUMNS,
            ]
        }
        opts["lower"] = convert_units(
            label=obj.label,
            value=obj.lower,
            units_from=obj.units,
            units_to=units,
            places=4,
        )
        opts["upper"] = convert_units(
            label=obj.label,
            value=obj.upper,
            units_from=obj.units,
            units_to=units,
            places=4,
        )
        opts["units"] = units
        opts["auto_created"] = True
        opts["created"] = timezone.now()
        opts["modified"] = opts["created"]
        break
    if opts:
        return normal_data_model_cls().objects.create(**opts)
    return None
