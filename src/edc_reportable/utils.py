from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Type

from django.conf import settings
from edc_utils import get_utcnow

from .constants import GRADE3, GRADE4

if TYPE_CHECKING:
    from .grade_reference import GradeReference
    from .normal_reference import NormalReference


def get_default_reportable_grades() -> list[str]:
    return getattr(settings, "EDC_REPORTABLE_DEFAULT_REPORTABLE_GRADES", [GRADE3, GRADE4])


def get_reference_range_collection_name(obj) -> str:
    """Returns the reference range name.

    Expects either a model with requisition attr or a requisition.
    """
    try:
        return obj.requisition.panel_object.reference_range_collection_name
    except AttributeError:
        return obj.panel_object.reference_range_collection_name


def get_normal_reference(
    name, units, gender, normal_references, exception_cls: Type[Exception] | None = None
):
    normal_reference = [
        x
        for x in normal_references or []
        if x.units == units
        and (gender in x.gender or gender == x.gender or gender in "".join(x.gender))
    ]
    if not normal_reference:
        raise exception_cls(
            f"Normal references not found. Need normal reference for {name} {units} {gender}. "
            f"Have {normal_references}"
        )
    elif len(normal_reference) > 1:
        raise exception_cls(
            "Multiple normal references found. " f"Got {name} {units} {gender}"
        )
    return normal_reference[0]


def get_references_by_criteria(
    value_references: list[NormalReference | GradeReference] = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    units: str = None,
    **extra_options,
):
    """Returns a list of references for this gender, age and units.

    Either ValueReferences or GradeReferences.
    """
    references = []
    report_datetime = report_datetime or get_utcnow()
    for value_reference in value_references:
        non_matching_opts = [
            k for k, v in extra_options.items() if getattr(value_reference, k) != v
        ]
        if (
            gender in value_reference.gender
            and value_reference.units == units
            and value_reference.age_match(dob, report_datetime)
            and not non_matching_opts
        ):
            references.append(value_reference)
    return references
