from django import forms
from django.conf import settings

from ..crf_date_validator import CrfDateValidator
from ..crf_date_validator import (
    CrfReportDateAllowanceError,
    CrfReportDateBeforeStudyStart,
)
from ..crf_date_validator import CrfReportDateIsFuture


class VisitTrackingModelFormMixin:
    """Validates subject visit and report datetime.

    Usually included in the form class declaration with
    `SubjectScheduleModelFormMixin`.
    """

    crf_date_validator_cls = CrfDateValidator
    report_datetime_allowance = getattr(
        settings, "DEFAULT_REPORT_DATETIME_ALLOWANCE", 0
    )

    def clean(self):
        """Triggers a validation error if subject visit is None.

        If subject visit, validate report_datetime.
        """
        cleaned_data = super().clean()

        # trigger a validation error if visit field is None
        # no comment needed since django will catch it as
        # a required field.
        if not self.subject_visit:
            raise forms.ValidationError({self.subject_visit_attr: ""})
        elif cleaned_data.get("report_datetime"):
            try:
                self.crf_date_validator_cls(
                    report_datetime_allowance=self.report_datetime_allowance,
                    report_datetime=cleaned_data.get("report_datetime"),
                    visit_report_datetime=cleaned_data.get(
                        self.subject_visit_attr
                    ).report_datetime,
                )
            except (
                CrfReportDateAllowanceError,
                CrfReportDateBeforeStudyStart,
                CrfReportDateIsFuture,
            ) as e:
                raise forms.ValidationError({"report_datetime": str(e)})
        return cleaned_data

    @property
    def subject_visit(self):
        return self.cleaned_data.get(self.subject_visit_attr)

    @property
    def subject_visit_attr(self):
        return self._meta.model.visit_model_attr()
