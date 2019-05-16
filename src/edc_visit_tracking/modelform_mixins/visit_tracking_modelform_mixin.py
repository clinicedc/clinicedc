from django import forms

from ..crf_date_validator import CrfDateValidator
from ..crf_date_validator import (
    CrfReportDateAllowanceError,
    CrfReportDateBeforeStudyStart,
)
from ..crf_date_validator import CrfReportDateIsFuture


class VisitTrackingModelFormError(Exception):
    pass


class VisitTrackingModelFormMixin:

    crf_validator_cls = CrfDateValidator
    visit_attr = None

    def clean(self):
        """Triggers a validation error if subject visit is None.

        If subject visit, validate report_datetime.
        """
        cleaned_data = super().clean()

        # trigger a validation error if visit field is None
        # no comment needed since django will catch it as
        # a required field.
        if not cleaned_data.get(self._meta.model.visit_model_attr()):
            raise forms.ValidationError(
                {self._meta.model.visit_model_attr(): ""})
        elif cleaned_data.get("report_datetime"):
            try:
                self.crf_validator_cls(
                    report_datetime=cleaned_data.get("report_datetime"),
                    visit_report_datetime=cleaned_data.get(
                        self._meta.model.visit_model_attr()
                    ).report_datetime,
                )
            except (
                CrfReportDateAllowanceError,
                CrfReportDateBeforeStudyStart,
                CrfReportDateIsFuture,
            ) as e:
                raise forms.ValidationError(e)
        return cleaned_data
