from __future__ import annotations

from typing import TYPE_CHECKING

from .grading_exception_model_cls import grading_exception_model_cls

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection

__all__ = ["update_grading_exceptions"]


def update_grading_exceptions(
    reference_range_collection: ReferenceRangeCollection,
    reportable_grades_exceptions: dict[str, list[str]] | None = None,
    keep_existing: bool | None = None,
):
    reportable_grades_exceptions = reportable_grades_exceptions or {}
    if not keep_existing:
        grading_exception_model_cls().objects.filter(
            reference_range_collection=reference_range_collection
        ).delete()
    for label, grades in reportable_grades_exceptions.items():
        grades = [int(g) for g in grades]
        grading_exception_model_cls().objects.get_or_create(
            reference_range_collection=reference_range_collection,
            label=label,
            grade1=True if 1 in grades else False,
            grade2=True if 2 in grades else False,
            grade3=True if 3 in grades else False,
            grade4=True if 4 in grades else False,
        )
