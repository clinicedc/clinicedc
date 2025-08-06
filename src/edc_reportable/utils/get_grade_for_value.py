from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from django.db.models import QuerySet

from ..exceptions import BoundariesOverlap, NotEvaluated, ValueBoundryError
from .get_normal_data_or_raise import get_normal_data_or_raise
from .grading_data_model_cls import grading_data_model_cls

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

    from ..models import GradingData, NormalData, ReferenceRangeCollection

__all__ = ["get_grade_for_value"]


def get_grade_for_value(
    reference_range_collection: ReferenceRangeCollection,
    value: float | int = None,
    label: str = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
    site: Site | None = None,
    create_missing_normal: bool | None = None,
) -> tuple[GradingData, str] | None:
    found_grading_data = None
    found_condition_str = None
    grading_data_objs = get_grading_data_instances(
        reference_range_collection=reference_range_collection,
        label=label,
        units=units,
        gender=gender,
        dob=dob,
        report_datetime=report_datetime,
        age_units=age_units,
    )
    for grading_data in grading_data_objs:
        normal_data = get_normal_data_or_raise(
            reference_range_collection=reference_range_collection,
            label=label,
            units=units,
            gender=gender,
            dob=dob,
            report_datetime=report_datetime,
            age_units=age_units,
            site=site,
            create_missing_normal=create_missing_normal,
        )
        lower_limit = get_lower_limit(normal_data, grading_data)
        upper_limit = get_upper_limit(normal_data, grading_data)
        value = float(value)
        condition_str = (
            f'{"" if lower_limit is None else lower_limit}'
            f'{grading_data.lower_operator or ""}{value}'
            f'{grading_data.upper_operator or ""}{"" if upper_limit is None else upper_limit}'
        )
        if eval(condition_str):  # nosec B307
            if not found_grading_data:
                found_grading_data = grading_data
                found_condition_str = (
                    f"{label}: {condition_str} {units} GRADE{grading_data.grade}"
                )
            else:
                raise BoundariesOverlap(
                    f"Overlapping grading definitions. Got {found_grading_data} "
                    f"which overlaps with {grading_data}. "
                    f"Using value={value} ({condition_str}). "
                    f"Check your grading definitions for `{label}` .",
                )
    return found_grading_data, found_condition_str


def get_lower_limit(
    normal_data: QuerySet[NormalData], grading_data: QuerySet[GradingData]
) -> int | float | None:
    lower_limit = float(grading_data.lower) if grading_data.lower else None
    if lower_limit and grading_data.lln:
        lower_limit = (
            lower_limit * normal_data.lower
            if "LLN" in grading_data.lln
            else lower_limit * normal_data.upper
        )
    return lower_limit


def get_upper_limit(
    normal_data: QuerySet[NormalData], grading_data: QuerySet[GradingData]
) -> int | float | None:
    upper_limit = float(grading_data.upper) if grading_data.upper else None
    if upper_limit and grading_data.uln:
        upper_limit = (
            upper_limit * normal_data.lower
            if "LLN" in grading_data.uln
            else upper_limit * normal_data.upper
        )
    return upper_limit


def get_grading_data_instances(
    reference_range_collection: ReferenceRangeCollection,
    label: str = None,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
    site: Site | None = None,
) -> list[GradingData]:
    if not gender:
        raise ValueError("Gender may not be None")
    grading_data_objs = []
    qs = (
        grading_data_model_cls()
        .objects.filter(
            reference_range_collection=reference_range_collection,
            label=label,
            units=units,
            gender=gender,
            # site=site,
        )
        .order_by("grade")
    )
    for obj in qs.all():
        try:
            age_in_bounds = obj.age_in_bounds_or_raise(
                dob=dob,
                report_datetime=report_datetime,
                age_units=age_units,
            )
        except ValueBoundryError:
            pass
        else:
            if age_in_bounds:
                grading_data_objs.append(obj)
    if not grading_data_objs:
        if qs.count() == 0:
            msg = f"No matching grading data found for {label} {units} {gender}"
        else:
            msg = (
                f"No matching grading data found for {label} {units} {gender} given age bounds"
            )
        raise NotEvaluated(f"Value not graded. {msg}")
    return grading_data_objs
