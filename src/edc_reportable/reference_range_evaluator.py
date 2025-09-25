from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from django import forms
from django.apps import apps as django_apps

from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_metadata.constants import REQUIRED

from .constants import ALREADY_REPORTED, INVALID_REFERENCE, PRESENT_AT_BASELINE
from .exceptions import NotEvaluated, ValueBoundryError
from .utils import get_grade_for_value, get_normal_data_or_raise

if TYPE_CHECKING:
    from .models import GradingData, NormalData, ReferenceRangeCollection


class UserFormResponse:
    def __init__(self, utest_id, cleaned_data=None):
        self.utest_id = utest_id
        # ensure each supporting option is provided from the form
        for attr in ["units", "abnormal", "reportable"]:
            if not cleaned_data.get(f"{utest_id}_{attr}"):
                raise forms.ValidationError(
                    {f"{utest_id}_{attr}": "This field is required."}, code=REQUIRED
                )

        self.abnormal = cleaned_data.get(f"{utest_id}_abnormal")
        self.reportable = cleaned_data.get(f"{utest_id}_reportable")
        self.units = cleaned_data.get(f"{utest_id}_units")

    def __repr__(self):
        return f"<UserResponse: {self.utest_id} ({self.units})>"

    def __str__(self):
        return f"{self.utest_id} ({self.units})"


class ReferenceRangeEvaluator:
    def __init__(
        self,
        reference_range_collection_name: str,
        cleaned_data: dict,
        gender: str,
        dob: date,
        report_datetime: datetime,
        age_units: str,
        value_field_suffix: str | None = None,
        **extra_options,
    ):
        if not self.reference_range_collection_model_cls.objects.filter(
            name=reference_range_collection_name
        ).exists():
            raise forms.ValidationError(
                {
                    "__all__": "Invalid reference range collection. "
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
        self.value_field_suffix = value_field_suffix or "_value"
        self.extra_options = extra_options

    def grades(self, utest_id: str) -> list[int]:
        return self.reference_range_collection.grades(utest_id)

    @property
    def reference_range_collection_model_cls(self) -> type[ReferenceRangeCollection]:
        return django_apps.get_model("edc_reportable.referencerangecollection")

    @property
    def normal_data_model_cls(self) -> type[NormalData]:
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
                    reference_range_collection=self.reference_range_collection,
                    label=utest_id,
                ).exists()
            ):
                # raise ValidationError if
                self._grade_or_check_normal_range(utest_id, value, field)

    def validate_results_abnormal_field(self):
        """Validate the "results_abnormal" field."""
        self._validate_final_assessment(
            field="results_abnormal",
            responses=[YES],
            suffix="_abnormal",
            word="abnormal",
        )

    def validate_results_reportable_field(self):
        """Validate the "results_reportable" field."""
        self._validate_final_assessment(
            field="results_reportable",
            responses=None,
            suffix="_reportable",
            word="reportable",
        )

    def _grade_or_check_normal_range(self, utest_id: str, value: int | float, field: str):
        """Evaluate a single result value.

        Grading is done first. If the value is not gradeable,
        the value is checked against the normal limits.

        Raise an exception if the user's response is discordant.

        Expected field naming convention:
            * {utest_id}_value
            * {utest_id}_units
            * {utest_id}_abnormal [YES, (NO)]
            * {utest_id}_reportable [(NOT_APPLICABLE), NO, GRADE3, GRADE4]
        """
        # get relevant user form reponses
        user_form_response = UserFormResponse(utest_id, self.cleaned_data)
        opts = dict(
            dob=self.dob,
            gender=self.gender,
            report_datetime=self.report_datetime,
            age_units=self.age_units,
            units=user_form_response.units,
            **self.extra_options,
        )
        grading_data, condition_str = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label=utest_id,
            value=value,
            **opts,
        )
        # is gradeable, user reponse matches grade or has valid opt out
        # response
        if (
            grading_data
            and grading_data.grade
            in self.reference_range_collection.reportable_grades(label=utest_id)
            and str(user_form_response.reportable)
            not in [
                str(grading_data.grade),
                ALREADY_REPORTED,
                PRESENT_AT_BASELINE,
            ]
        ):
            raise forms.ValidationError(
                {
                    field: (
                        f"{utest_id.upper()} is reportable. Got {grading_data.description}. "
                        f"({condition_str})."
                    )
                }
            )
        # user selects grade that does not match grade from evaluator
        if (
            grading_data
            and grading_data.grade
            and str(user_form_response.reportable) in [str(g) for g in self.grades(utest_id)]
            and str(grading_data.grade) != str(user_form_response.reportable)
        ):
            raise forms.ValidationError(
                {
                    field: (
                        f"{utest_id.upper()} grade mismatch. Value given evaluates to grade "
                        f"{grading_data.grade} ({condition_str}). "
                        f"Got grade {user_form_response.reportable}. "
                    )
                }
            )

        # is not gradeable, user reponse is a valid `opt out`.
        if not grading_data and str(user_form_response.reportable) not in [
            NO,
            NOT_APPLICABLE,
        ]:
            raise forms.ValidationError(
                {f"{utest_id}_reportable": "Invalid. Expected 'No' or 'Not applicable'."}
            )
        self._check_normal_range(
            utest_id=utest_id,
            value=value,
            field=field,
            grading_data=grading_data,
            user_form_response=user_form_response,
            opts=opts,
        )

    def _check_normal_range(
        self,
        *,
        utest_id: str,
        value: int | float,
        field: str,
        grading_data: GradingData,
        user_form_response: UserFormResponse,
        opts: dict,
    ):
        try:
            normal_data = get_normal_data_or_raise(
                reference_range_collection=self.reference_range_collection,
                label=utest_id,
                **opts,
            )
        except NotEvaluated as e:
            raise forms.ValidationError({field: str(e)}) from e
        else:
            try:
                is_normal = normal_data.value_in_normal_range_or_raise(
                    value=value,
                    dob=self.dob,
                    report_datetime=self.report_datetime,
                    age_units=self.age_units,
                )
            except ValueBoundryError:
                is_normal = False
            # is not normal, user response does not match
            if not is_normal and user_form_response.abnormal == NO:
                raise forms.ValidationError(
                    {
                        field: (
                            f"{utest_id.upper()} is abnormal. "
                            f"Normal range: {normal_data.description}"
                        )
                    }
                )

            # is not normal and not gradeable, user response does not match
            if is_normal and not grading_data and user_form_response.abnormal == YES:
                raise forms.ValidationError(
                    {f"{utest_id}_abnormal": "Invalid. Result is not abnormal"}
                )

            # illogical user response combination
            if (
                user_form_response.abnormal == YES
                and user_form_response.reportable == NOT_APPLICABLE
            ):
                raise forms.ValidationError(
                    {
                        f"{utest_id}_reportable": (
                            "This field is applicable if result is abnormal"
                        )
                    }
                )

            # illogical user response combination
            if (
                user_form_response.abnormal == NO
                and user_form_response.reportable != NOT_APPLICABLE
            ):
                raise forms.ValidationError(
                    {f"{utest_id}_reportable": "This field is not applicable"}
                )

    def _validate_final_assessment(
        self, *, field: str, suffix: str, word: str, responses: list[str] | None = None
    ):
        """Common code to validate fields `results_abnormal`
        and `results_reportable`.
        """
        responses = responses or [
            str(g) for g in self.reference_range_collection.default_grades()
        ]
        responses = [str(r) for r in responses]
        answers = list(
            {k: v for k, v in self.cleaned_data.items() if k.endswith(suffix)}.values()
        )
        answers = [str(v) for v in answers if v is not None]
        if len(answers) == 0:
            raise forms.ValidationError({"results_abnormal": "No results have been entered."})
        answers_as_bool = [True for v in answers if v in responses]
        if self.cleaned_data.get(field) == NO:
            if any(answers_as_bool):
                are = "is" if len(answers_as_bool) == 1 else "are"
                raise forms.ValidationError(
                    {field: f"{len(answers_as_bool)} of the above results {are} {word}"}
                )
        elif self.cleaned_data.get(field) == YES and not any(answers_as_bool):
            raise forms.ValidationError({field: f"None of the above results are {word}"})
