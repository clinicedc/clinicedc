from typing import Any

from django import forms
from django.conf import settings

from ..crf_date_validator import (
    CrfDateValidator,
    CrfReportDateAllowanceError,
    CrfReportDateBeforeStudyStart,
    CrfReportDateIsFuture,
)
from .utils import get_related_visit


class VisitTrackingModelFormMixin:
    """Validates subject visit and report datetime.

    Usually included in the form class declaration with
    `CRfScheduleModelFormMixin`.
    """

    crf_date_validator_cls = CrfDateValidator
    report_datetime_allowance = getattr(settings, "DEFAULT_REPORT_DATETIME_ALLOWANCE", 0)

    # may also be appt_datetime or requisition_datetime
    report_datetime_field_attr = "report_datetime"

    def clean(self: Any) -> dict:
        """Triggers a validation error if subject visit is None.

        If subject visit, validate report_datetime.
        """
        cleaned_data = super().clean()  # type: ignore

        self.validate_visit_tracking()

        return cleaned_data

    def validate_visit_tracking(self: Any) -> None:
        # trigger a validation error if visit field is None
        # no comment needed since django will catch it as
        # a required field.
        if not self.related_visit:
            if self.related_visit_model_attr() in self.cleaned_data:
                raise forms.ValidationError({self.related_visit_model_attr(): ""})
            else:
                raise forms.ValidationError(
                    f"Field `{self.related_visit_model_attr()}` is required (1)."
                )
        elif self.cleaned_data.get(self.report_datetime_field_attr):
            try:
                self.crf_date_validator_cls(
                    report_datetime_allowance=self.report_datetime_allowance,
                    report_datetime=self.cleaned_data.get(self.report_datetime_field_attr),
                    visit_report_datetime=self.related_visit.report_datetime,
                )
            except (
                CrfReportDateAllowanceError,
                CrfReportDateBeforeStudyStart,
                CrfReportDateIsFuture,
            ) as e:
                raise forms.ValidationError({self.report_datetime_field_attr: str(e)})

    @property
    def related_visit(self: Any) -> Any:
        return get_related_visit(
            self, related_visit_model_attr=self.related_visit_model_attr()
        )

    def related_visit_model_attr(self: Any) -> str:
        return self._meta.model.related_visit_model_attr()
