from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from ..exceptions import NotEvaluated
from ..formula import Formula
from .get_default_reportable_grades import get_default_reportable_grades
from .get_grade_for_value import get_grade_for_value
from .grading_data_model_cls import grading_data_model_cls
from .grading_exception_model_cls import grading_exception_model_cls

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection


__all__ = ["update_grading_data"]


def update_grading_data(
    reference_range_collection: ReferenceRangeCollection,
    grading_data: dict[str, list[Formula]] | None = None,
    reportable_grades: list[str] | None = None,
    reportable_grades_exceptions: dict[str, list[str]] | None = None,
    keep_existing: bool | None = None,
    create_missing_normal: bool | None = None,
):
    if not keep_existing:
        grading_data_model_cls().objects.filter(
            reference_range_collection=reference_range_collection
        ).delete()
    for label, formulas in grading_data.items():
        for formula in formulas:
            if get_reportable_grades(reference_range_collection, label, reportable_grades):
                formula_opts = {k: v for k, v in formula.__dict__.items() if k != "gender"}
                age_opts = {k: v for k, v in formula_opts.items() if "age" in k}
                for gender in formula.__dict__.get("gender"):
                    grading_data_model_cls().objects.create(
                        reference_range_collection=reference_range_collection,
                        label=label,
                        description=formula.description,
                        gender=gender,
                        **formula_opts,
                    )
                    for value in [formula.lower, formula.upper]:
                        if value:
                            try:
                                get_grade_for_value(
                                    reference_range_collection=reference_range_collection,
                                    label=label,
                                    value=value,
                                    units=formula_opts.get("units"),
                                    gender=gender,
                                    dob=timezone.now()
                                    - relativedelta(
                                        **{
                                            age_opts.get("age_units"): age_opts.get(
                                                "age_lower"
                                            )
                                        }
                                    ),
                                    report_datetime=timezone.now(),
                                    age_units=age_opts.get("age_units"),
                                    create_missing_normal=create_missing_normal,
                                )
                            except NotEvaluated as e:
                                sys.stdout.write(f"{e}\n")


def get_reportable_grades(
    reference_range_collection: ReferenceRangeCollection, label, reportable_grades
) -> list[int]:
    try:
        grading_exception = grading_exception_model_cls().objects.get(
            reference_range_collection=reference_range_collection, label=label
        )
    except ObjectDoesNotExist:
        reportable_grades = reportable_grades or get_default_reportable_grades()
    else:
        reportable_grades = grading_exception.grades.split(",")
    return reportable_grades
