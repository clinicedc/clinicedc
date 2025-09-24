from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import forms
from django.conf import settings

from edc_form_validators import INVALID_ERROR

from ...crf_date_validator import (
    CrfDateValidator,
    CrfReportDateAllowanceError,
    CrfReportDateBeforeStudyStart,
    CrfReportDateIsFuture,
)
from ...visit_sequence import VisitSequence, VisitSequenceError
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
    visit_sequence_cls = VisitSequence

    def clean(self: Any) -> dict:
        """Triggers a validation error if subject visit is None.

        If subject visit, validate report_datetime.
        """
        if not self.report_datetime_field_attr:
            raise VisitTrackingCrfModelFormMixinError(
                f"Cannot be None. See modelform for {self._meta.model}."
                "Got `report_datetime_field_attr`=None."
            )
        cleaned_data = super().clean()
        self.validate_visits_completed_in_order()
        self.validate_visit_tracking()
        return cleaned_data

    def get_subject_identifier(self):
        """Overridden"""
        return self.related_visit.subject_identifier

    @property
    def related_visit(self) -> VisitModelMixin | None:
        related_model_cls = getattr(self._meta.model, self.related_visit_model_attr)
        if not related_model_cls:
            raise VisitTrackingCrfModelFormMixinError(
                "Model requires an FK to the related visit model. Is this a CRF? "
                f"See model {self._meta.model}"
            )
        try:
            related_visit = get_related_visit(
                self, related_visit_model_attr=self.related_visit_model_attr
            )
        except getattr(
            self._meta.model, self.related_visit_model_attr
        ).RelatedObjectDoesNotExist:
            related_visit = None
        return related_visit

    @property
    def related_visit_model_attr(self) -> str:
        try:
            return self._meta.model.related_visit_model_attr()
        except AttributeError as e:
            raise VisitTrackingCrfModelFormMixinError(
                "Expected method `related_visit_model_attr`. Is this a CRF? "
                f"See model {self._meta.model}"
            ) from e

    def validate_visit_tracking(self: Any) -> None:
        # trigger a validation error if visit field is None
        # no comment needed since django will catch it as
        # a required field.
        if not self.related_visit:
            if self.related_visit_model_attr in self.cleaned_data:
                raise forms.ValidationError({self.related_visit_model_attr: ""})
            raise forms.ValidationError(
                f"Field `{self.related_visit_model_attr}` is required (1)."
            )
        if self.cleaned_data.get(self.report_datetime_field_attr):
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
                raise forms.ValidationError({self.report_datetime_field_attr: str(e)}) from e

    def validate_visits_completed_in_order(self) -> None:
        """Asserts visits are completed in order."""
        if self.related_visit:
            visit_sequence = self.visit_sequence_cls(
                appointment=self.related_visit.appointment
            )
            try:
                visit_sequence.enforce_sequence(document_type="CRF")
            except VisitSequenceError as e:
                raise forms.ValidationError(str(e), code=INVALID_ERROR) from e
