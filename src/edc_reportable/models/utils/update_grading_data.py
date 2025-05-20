from __future__ import annotations

from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow

from ...exceptions import NotEvaluated
from ...formula import Formula
from ...utils import get_default_reportable_grades
from ..grading_data import GradingData
from ..grading_exception import GradingException
from .get_grade_for_value import get_grade_for_value

if TYPE_CHECKING:
    from ..reference_range_collection import ReferenceRangeCollection


def update_grading_exceptions(
    reference_range_collection: ReferenceRangeCollection,
    reportable_grades_exceptions: dict[str, list[str]] | None = None,
    keep_existing: bool | None = None,
):
    reportable_grades_exceptions = reportable_grades_exceptions or {}
    if not keep_existing:
        GradingException.objects.filter(
            reference_range_collection=reference_range_collection
        ).delete()
    for label, grades in reportable_grades_exceptions.items():
        grades = [int(g) for g in grades]
        GradingException.objects.get_or_create(
            reference_range_collection=reference_range_collection,
            label=label,
            grade1=True if 1 in grades else False,
            grade2=True if 2 in grades else False,
            grade3=True if 3 in grades else False,
            grade4=True if 4 in grades else False,
        )


def update_grading_data(
    reference_range_collection: ReferenceRangeCollection,
    grading_data: dict[str, list[Formula]] | None = None,
    reportable_grades: list[str] | None = None,
    reportable_grades_exceptions: dict[str, list[str]] | None = None,
    keep_existing: bool | None = None,
):
    reportable_grades = reportable_grades or get_default_reportable_grades()
    for grade in reportable_grades:
        setattr(reference_range_collection, f"GRADE{grade}", True)
    reference_range_collection.save()

    update_grading_exceptions(
        reference_range_collection=reference_range_collection,
        reportable_grades_exceptions=reportable_grades_exceptions,
        keep_existing=keep_existing,
    )
    if not keep_existing:
        GradingData.objects.filter(
            reference_range_collection=reference_range_collection
        ).delete()
    for label, formulas in grading_data.items():
        for formula in formulas:
            if get_reportable_grades(reference_range_collection, label, reportable_grades):
                formula_opts = {k: v for k, v in formula.__dict__.items() if k != "gender"}
                age_opts = {k: v for k, v in formula_opts.items() if "age" in k}
                for gender in formula.__dict__.get("gender"):
                    GradingData.objects.create(
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
                                    dob=get_utcnow()
                                    - relativedelta(
                                        **{
                                            age_opts.get("age_units"): age_opts.get(
                                                "age_lower"
                                            )
                                        }
                                    ),
                                    report_datetime=get_utcnow(),
                                    age_units=age_opts.get("age_units"),
                                )
                            except NotEvaluated as e:
                                print(e)


def get_reportable_grades(
    reference_range_collection: ReferenceRangeCollection, label, reportable_grades
) -> list[int]:
    try:
        grading_exception = GradingException.objects.get(
            reference_range_collection=reference_range_collection, label=label
        )
    except ObjectDoesNotExist:
        reportable_grades = reportable_grades or get_default_reportable_grades()
    else:
        reportable_grades = grading_exception.grades.split(",")
    return reportable_grades
