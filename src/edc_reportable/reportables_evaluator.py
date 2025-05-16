from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Type

from django import forms
from django.apps import apps as django_apps
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_metadata.constants import REQUIRED

from .constants import (
    ALREADY_REPORTED,
    GRADE0,
    GRADE1,
    GRADE2,
    GRADE3,
    GRADE4,
    INVALID_REFERENCE,
    PRESENT_AT_BASELINE,
)
from .exceptions import NotEvaluated, ValueBoundryError
from .models import get_grade_for_value, get_normal_data_or_raise

if TYPE_CHECKING:
    from .models import NormalData, ReferenceRangeCollection


class UserResponse:
    def __init__(self, utest_id, cleaned_data=None):
        # ensure each supporting option is provided from the form
        for attr in ["units", "abnormal", "reportable"]:
            if not cleaned_data.get(f"{utest_id}_{attr}"):
                raise forms.ValidationError(
                    {f"{utest_id}_{attr}": "This field is required."}, code=REQUIRED
                )

        self.abnormal = cleaned_data.get(f"{utest_id}_abnormal")
        self.reportable = cleaned_data.get(f"{utest_id}_reportable")
        self.units = cleaned_data.get(f"{utest_id}_units")


class ReportablesEvaluator:
    def __init__(
        self,
        reference_range_collection_name=None,
        cleaned_data=None,
        gender: str = None,
        dob: date = None,
        report_datetime: datetime = None,
        age_units: str | None = None,
        value_field_suffix=None,
        **extra_options,
    ):
        if not self.reference_range_collection_model_cls.objects.filter(
            name=reference_range_collection_name
        ).exists():
            raise forms.ValidationError(
                {
                    "Invalid reference range collection. "
                    f"Got '{reference_range_collection_name}'"
                },
                code=INVALID_REFERENCE,
            )
        self.reference_range_collection = (
            self.reference_range_collection_model_cls.objects.get(
                name=reference_range_collection_name
            )
        )
        self.cleaned_data = cleaned_data
        self.dob = dob
        self.gender = gender
        self.report_datetime = report_datetime
        self.age_units = age_units
        self.value_field_suffix = value_field_suffix
        self.extra_options = extra_options

    @property
    def grades(self) -> list[str]:
        return [GRADE0, GRADE1, GRADE2, GRADE3, GRADE4]

    @property
    def reference_range_collection_model_cls(self) -> Type[ReferenceRangeCollection]:
        return django_apps.get_model("edc_reportable.referencerangecollection")

    @property
    def normal_data_model_cls(self) -> Type[NormalData]:
        return django_apps.get_model("edc_reportable.normaldata")

    def validate_reportable_fields(self):
        """Check normal ranges and grade result values
        for each field mentioned in the reference_range_collection.
        """
        for field, value in self.cleaned_data.items():
            try:
                utest_id, _ = field.split(self.value_field_suffix)
            except ValueError:
                utest_id = field
            if (
                value is not None
                and self.normal_data_model_cls.objects.filter(
                    reference_range_collection=self.reference_range_collection, label=utest_id
                ).exists()
            ):
                self._grade_or_check_normal_range(utest_id, value, field)

    def validate_results_abnormal_field(
        self, field=None, responses=None, suffix=None, word=None
    ):
        """Validate the "results_abnormal" field."""
        self._validate_final_assessment(
            field=field or "results_abnormal",
            responses=responses or [YES],
            suffix=suffix or "_abnormal",
            word=word or "abnormal",
        )

    def validate_results_reportable_field(
        self, field=None, responses=None, suffix=None, word=None
    ):
        """Validate the "results_reportable" field."""
        self._validate_final_assessment(
            field=field or "results_reportable",
            responses=responses,
            suffix=suffix or "_reportable",
            word=word or "reportable",
        )

    def _grade_or_check_normal_range(self, utest_id, value, field):
        """Evaluate a single result value.

        Grading is done first. If the value is not gradeable,
        the value is checked against the normal limits.

        Expected field naming convention:
            * {utest_id}_value
            * {utest_id}_units
            * {utest_id}_abnormal [YES, (NO)]
            * {utest_id}_reportable [(NOT_APPLICABLE), NO, GRADE3, GRADE4]
        """
        # get relevant user form reponses
        response = UserResponse(utest_id, self.cleaned_data)
        opts = dict(
            dob=self.dob,
            gender=self.gender,
            report_datetime=self.report_datetime,
            age_units=self.age_units,
            units=response.units,
            **self.extra_options,
        )
        grade = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label=utest_id,
            value=value,
            **opts,
        )
        # is gradeable, user reponse matches grade or has valid opt out
        # response
        if (
            grade
            and grade.grade
            and str(grade.grade) in self.reference_range_collection.reportable_grades(utest_id)
            and response.reportable
            not in [str(grade.grade), ALREADY_REPORTED, PRESENT_AT_BASELINE]
        ):
            raise forms.ValidationError(
                {field: f"{utest_id.upper()} is reportable. Got {grade.description}."}
            )
        # user selects grade that does not match grade from evaluator
        if (
            grade
            and grade.grade
            and response.reportable in self.grades
            and str(grade.grade) != str(response.reportable)
        ):
            raise forms.ValidationError(
                {
                    field: (
                        f"{utest_id.upper()} grade mismatch. Evaluated as grade "
                        f"{grade.grade}. Got {response.reportable}."
                    )
                }
            )

        # is not gradeable, user reponse is a valid `opt out`.
        if not grade and response.reportable not in [NO, NOT_APPLICABLE]:
            raise forms.ValidationError(
                {f"{utest_id}_reportable": "Invalid. Expected 'No' or 'Not applicable'."}
            )
        self._check_normal_range(utest_id, value, field, grade, response, opts)

    def _check_normal_range(self, utest_id, value, field, grade, response, opts):
        try:
            normal_data = get_normal_data_or_raise(
                reference_range_collection=self.reference_range_collection,
                label=utest_id,
                **opts,
            )
        except NotEvaluated as e:
            raise forms.ValidationError({field: str(e)})
        else:
            try:
                normal = normal_data.value_in_normal_range_or_raise(
                    value=value,
                    dob=self.dob,
                    report_datetime=self.report_datetime,
                    age_units=self.age_units,
                )
            except ValueBoundryError:
                normal = False
            # is not normal, user response does not match
            if not normal and response.abnormal == NO:
                raise forms.ValidationError(
                    {
                        field: (
                            f"{utest_id.upper()} is abnormal. "
                            f"Normal range: {normal_data.description}"
                        )
                    }
                )

            # is not normal and not gradeable, user response does not match
            if normal and not grade and response.abnormal == YES:
                raise forms.ValidationError(
                    {f"{utest_id}_abnormal": "Invalid. Result is not abnormal"}
                )

            # illogical user response combination
            if response.abnormal == YES and response.reportable == NOT_APPLICABLE:
                raise forms.ValidationError(
                    {
                        f"{utest_id}_reportable": (
                            "This field is applicable if result is abnormal"
                        )
                    }
                )

            # illogical user response combination
            if response.abnormal == NO and response.reportable != NOT_APPLICABLE:
                raise forms.ValidationError(
                    {f"{utest_id}_reportable": "This field is not applicable"}
                )

    def _validate_final_assessment(self, field=None, responses=None, suffix=None, word=None):
        """Common code to validate fields `results_abnormal`
        and `results_reportable`.
        """
        responses = responses or self.reference_range_collection.reportable_grades
        answers = list(
            {k: v for k, v in self.cleaned_data.items() if k.endswith(suffix)}.values()
        )
        if len([True for v in answers if v is not None]) == 0:
            raise forms.ValidationError({"results_abnormal": "No results have been entered."})
        answers_as_bool = [True for v in answers if v in responses]
        if self.cleaned_data.get(field) == NO:
            if any(answers_as_bool):
                are = "is" if len(answers_as_bool) == 1 else "are"
                raise forms.ValidationError(
                    {field: f"{len(answers_as_bool)} of the above results {are} {word}"}
                )
        elif self.cleaned_data.get(field) == YES:
            if not any(answers_as_bool):
                raise forms.ValidationError({field: f"None of the above results are {word}"})
