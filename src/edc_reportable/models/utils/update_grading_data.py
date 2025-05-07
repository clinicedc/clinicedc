from __future__ import annotations

from typing import TYPE_CHECKING

from ...formula import Formula
from ...utils import get_default_reportable_grades
from ..grading_data import GradingData

if TYPE_CHECKING:
    from ..reference_range_collection import ReferenceRangeCollection


def update_grading_data(
    reference_range_collection: ReferenceRangeCollection,
    grading_data: dict[str, list[Formula]] | None = None,
    reportable_grades: list[str] | None = None,
    reportable_grades_exceptions: dict[str, list[str]] | None = None,
):
    reportable_grades = reportable_grades or get_default_reportable_grades()
    reportable_grades_exceptions = reportable_grades_exceptions or {}
    GradingData.objects.filter(reference_range_collection=reference_range_collection).delete()
    for label, formulas in grading_data.items():
        for formula in formulas:
            if (
                formula.grade in (reportable_grades_exceptions.get(label) or [])
                or reportable_grades
            ):
                opts = {k: v for k, v in formula.__dict__.items() if k != "gender"}
                for gender in formula.__dict__.get("gender"):
                    GradingData.objects.create(
                        reference_range_collection=reference_range_collection,
                        label=label,
                        description=formula.description,
                        gender=gender,
                        **opts,
                    )
