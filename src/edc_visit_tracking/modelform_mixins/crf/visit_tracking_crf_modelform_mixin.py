from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings

from ...crf_date_validator import (
    CrfDateValidator,
    CrfReportDateAllowanceError,
    CrfReportDateBeforeStudyStart,
    CrfReportDateIsFuture,
)
from ..utils import get_related_visit

if TYPE_CHECKING:
    from ...model_mixins import VisitModelMixin


class VisitTrackingCrfModelFormMixinError(Exception):
    pass


class VisitTrackingCrfModelFormMixin:
    """Validates subject visit and report datetime.

    Usually included in the form class declaration with
    `CRfScheduleModelFormMixin`.
    """

    crf_date_validator_cls = CrfDateValidator
    report_datetime_allowance = getattr(settings, "DEFAULT_REPORT_DATETIME_ALLOWANCE", 0)

    def clean(self: Any) -> dict:
        """Triggers a validation error if subject visit is None.

        If subject visit, validate report_datetime.
        """
        if not self.report_datetime_field_attr:
            raise VisitTrackingCrfModelFormMixinError(
                f"Cannot be None. See modeform for {self._meta.model}."
                "Got `report_datetime_field_attr`=None."
            )
        cleaned_data = super().clean()
        self.validate_visit_tracking()
        return cleaned_data

    @property
    def subject_identifier(self):
        """Overridden"""
        return (
            self.cleaned_data.get("subject_identifier")
            or self.related_visit.subject_identifier
        )

    @property
    def report_datetime(self) -> datetime:
        """Overridden. Returns the report_datetime as UTC from directly from
        cleaned_data or via the related_visit, if it exists.
        """
        report_datetime = self.cleaned_data.get(self.report_datetime_field_attr)
        if self.related_visit and not report_datetime:
            report_datetime = getattr(self.related_visit, self.report_datetime_field_attr)
        if report_datetime:
            report_datetime = report_datetime.astimezone(ZoneInfo("UTC"))
        return report_datetime

    def validate_visit_tracking(self: Any) -> None:
        # trigger a validation error if visit field is None
        # no comment needed since django will catch it as
        # a required field.
        if not self.related_visit:
            if self.related_visit_model_attr in self.cleaned_data:
                raise forms.ValidationError({self.related_visit_model_attr: ""})
            else:
                raise forms.ValidationError(
                    f"Field `{self.related_visit_model_attr}` is required (1)."
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
    def related_visit(self) -> VisitModelMixin | None:
        return get_related_visit(self, related_visit_model_attr=self.related_visit_model_attr)

    @property
    def related_visit_model_attr(self) -> str:
        try:
            return self._meta.model.related_visit_model_attr()
        except AttributeError:
            raise VisitTrackingCrfModelFormMixinError(
                "Expected method `related_visit_model_attr`. Is this a CRF? "
                f"See model {self._meta.model}"
            )
