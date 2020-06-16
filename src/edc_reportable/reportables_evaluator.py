from django import forms
from edc_constants.constants import NOT_APPLICABLE, NO, YES
from edc_metadata.constants import REQUIRED

from .constants import (
    ALREADY_REPORTED,
    PRESENT_AT_BASELINE,
    GRADE2,
    GRADE3,
    GRADE4,
    INVALID_REFERENCE,
)
from .site_reportables import site_reportables
from .value_reference_group import NotEvaluated


class UserResponse:
    def __init__(self, field, cleaned_data=None):
        # ensure each supporting option is provided from the form
        for attr in ["units", "abnormal", "reportable"]:
            if not cleaned_data.get(f"{field}_{attr}"):
                raise forms.ValidationError(
                    {f"{field}_{attr}": "This field is required."}, code=REQUIRED
                )

        self.abnormal = cleaned_data.get(f"{field}_abnormal")
        self.reportable = cleaned_data.get(f"{field}_reportable")
        self.units = cleaned_data.get(f"{field}_units")


class ReportablesEvaluator:
    def __init__(
        self,
        reference_list_name=None,
        cleaned_data=None,
        gender=None,
        dob=None,
        report_datetime=None,
        **extra_options,
    ):
        self.reference_list = site_reportables.get(reference_list_name)
        if not self.reference_list:
            raise forms.ValidationError(
                {f"Invalid reference list. Got '{reference_list_name}'"},
                code=INVALID_REFERENCE,
            )

        self.cleaned_data = cleaned_data
        self.dob = dob
        self.gender = gender
        self.report_datetime = report_datetime
        self.extra_options = extra_options

    def validate_reportable_fields(self):
        """Check normal ranges and grade result values
        for each field mentioned in the reference_list.
        """
        for field, value in self.cleaned_data.items():
            if value is not None and self.reference_list.get(field):
                self._evaluate_reportable(field, value)

    def validate_results_abnormal_field(
        self, field=None, responses=None, suffix=None, word=None
    ):
        """Validate the "results_abnormal" field.
        """
        self._validate_final_assessment(
            field=field or "results_abnormal",
            responses=responses or [YES],
            suffix=suffix or "_abnormal",
            word=word or "abnormal",
        )

    def validate_results_reportable_field(
        self, field=None, responses=None, suffix=None, word=None
    ):
        """Validate the "results_reportable" field.
        """
        self._validate_final_assessment(
            field=field or "results_reportable",
            responses=responses or [GRADE2, GRADE3, GRADE4],
            suffix=suffix or "_reportable",
            word=word or "reportable",
        )

    def _evaluate_reportable(self, field, value):
        """Evaluate a single result value.

        Grading is done first. If the value is not gradeable,
        the value is checked against the normal limits.

        Expected field naming convention:
            * {field}
            * {field}_units
            * {field}_abnormal [YES, (NO)]
            * {field}_reportable [(NOT_APPLICABLE), NO, GRADE3, GRADE4]
        """

        # get relevant user form reponses
        response = UserResponse(field, self.cleaned_data)

        opts = dict(
            dob=self.dob,
            gender=self.gender,
            report_datetime=self.report_datetime,
            units=response.units,
            **self.extra_options,
        )

        grade = self.get_grade(field, value, **opts)

        # is gradeable, user reponse matches grade or has valid opt out
        # response
        if (
            grade
            and grade.grade
            and response.reportable
            not in [str(grade.grade), ALREADY_REPORTED, PRESENT_AT_BASELINE]
        ):
            raise forms.ValidationError(
                {field: f"{field.upper()} is reportable. Got {grade.description}."}
            )

        # is not gradeable, user reponse is a valid opt out
        if not grade and response.reportable not in [NO, NOT_APPLICABLE]:
            raise forms.ValidationError(
                {f"{field}_reportable": "Invalid. Expected 'No' or 'Not applicable'."}
            )

        normal = self.get_normal(field, value, **opts)

        # is not normal, user response does not match
        if not normal and response.abnormal == NO:
            descriptions = self.reference_list.get(field).get_normal_description(**opts)
            raise forms.ValidationError(
                {
                    field: (
                        f"{field.upper()} is abnormal. "
                        f"Normal ranges: {', '.join(descriptions)}"
                    )
                }
            )

        # is not normal and not gradeable, user response does not match
        if normal and not grade and response.abnormal == YES:
            raise forms.ValidationError(
                {f"{field}_abnormal": "Invalid. Result is not abnormal"}
            )

        # illogical user response combination
        if response.abnormal == YES and response.reportable == NOT_APPLICABLE:
            raise forms.ValidationError(
                {
                    f"{field}_reportable": (
                        "This field is applicable if result is abnormal"
                    )
                }
            )

        # illogical user response combination
        if response.abnormal == NO and response.reportable != NOT_APPLICABLE:
            raise forms.ValidationError(
                {f"{field}_reportable": "This field is not applicable"}
            )

    def get_grade(self, field, value, **opts):
        try:
            grade = self.reference_list.get(field).get_grade(value, **opts)
        except NotEvaluated as e:
            raise forms.ValidationError({field: str(e)})
        return grade

    def get_normal(self, field, value, **opts):
        try:
            normal = self.reference_list.get(field).get_normal(value, **opts)
        except NotEvaluated as e:
            raise forms.ValidationError({field: str(e)})
        return normal

    def _validate_final_assessment(
        self, field=None, responses=None, suffix=None, word=None
    ):
        """Common code to validate fields `results_abnormal`
        and `results_reportable`.
        """
        answers = list(
            {k: v for k, v in self.cleaned_data.items() if k.endswith(suffix)}.values()
        )
        if len([True for v in answers if v is not None]) == 0:
            raise forms.ValidationError(
                {"results_abnormal": "No results have been entered."}
            )
        answers_as_bool = [True for v in answers if v in responses]
        if self.cleaned_data.get(field) == NO:
            if any(answers_as_bool):
                are = "is" if len(answers_as_bool) == 1 else "are"
                raise forms.ValidationError(
                    {field: f"{len(answers_as_bool)} of the above results {are} {word}"}
                )
        elif self.cleaned_data.get(field) == YES:
            if not any(answers_as_bool):
                raise forms.ValidationError(
                    {field: f"None of the above results are {word}"}
                )
