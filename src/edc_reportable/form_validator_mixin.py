from django import forms
from edc_constants.constants import NOT_APPLICABLE, NO, YES

from .constants import ALREADY_REPORTED, PRESENT_AT_BASELINE
from .value_reference_group import NotEvaluated


class ReportablesFormValidatorMixin:
    def evaluate_reportable(self, field, value, grp, **opts):
        """Evaluate a single result value.

        Grading is done first. If the value is not gradeable,
        the value is checked against the normal limits.

        Expected field naming convention:
            * {field}
            * {field}_units
            * {field}_abnormal [YES, (NO)]
            * {field}_reportable [(NOT_APPLICABLE), NO, GRADE3, GRADE4]
        """
        abnormal = self.cleaned_data.get(f"{field}_abnormal")
        reportable = self.cleaned_data.get(f"{field}_reportable")
        units = self.cleaned_data.get(f"{field}_units")
        opts.update(units=units)
        if not units:
            raise forms.ValidationError({f"{field}_units": f"Units required."})
        try:
            grade = grp.get_grade(value, **opts)
        except NotEvaluated as e:
            raise forms.ValidationError({field: str(e)})

        if grade and grade.grade and reportable != str(grade.grade):
            if reportable not in [ALREADY_REPORTED, PRESENT_AT_BASELINE]:
                raise forms.ValidationError(
                    {field: f"{field.upper()} is reportable. Got {grade.description}."}
                )
        elif not grade and reportable not in [NO, NOT_APPLICABLE]:
            raise forms.ValidationError(
                {f"{field}_reportable": "Invalid. Expected 'No' or 'Not applicable'."}
            )
        else:
            try:
                normal = grp.get_normal(value, **opts)
            except NotEvaluated as e:
                raise forms.ValidationError({field: str(e)})
            if not normal and abnormal == NO:
                descriptions = grp.get_normal_description(**opts)
                raise forms.ValidationError(
                    {
                        field: (
                            f"{field.upper()} is abnormal. "
                            f"Normal ranges: {', '.join(descriptions)}"
                        )
                    }
                )
            elif normal and not grade and abnormal == YES:
                raise forms.ValidationError(
                    {f"{field}_abnormal": "Invalid. Result is not abnormal"}
                )

        if abnormal == YES and reportable == NOT_APPLICABLE:
            raise forms.ValidationError(
                {
                    f"{field}_reportable": (
                        "This field is applicable if " "result is abnormal"
                    )
                }
            )
        elif abnormal == NO and reportable != NOT_APPLICABLE:
            raise forms.ValidationError(
                {f"{field}_reportable": "This field is not applicable"}
            )
