from __future__ import annotations

import warnings
from datetime import datetime
from typing import TYPE_CHECKING

from edc_appointment.form_validators import WindowPeriodFormValidatorMixin
from edc_consent.form_validators import ConsentFormValidatorMixin
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_registration import get_registered_subject_model_cls
from edc_utils import formatted_datetime
from edc_visit_tracking.modelform_mixins import get_related_visit

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_visit_tracking.model_mixins import VisitModelMixin


class CrfFormValidator(
    WindowPeriodFormValidatorMixin, ConsentFormValidatorMixin, FormValidator
):
    """Form validator for CRfs.

    CRFs have a FK to subject_visit.
    """

    report_datetime_field_attr = "report_datetime"

    def _clean(self) -> None:
        self.validate_crf_report_datetime()
        super()._clean()

    def validate_crf_report_datetime(self) -> None:
        if self.cleaned_data.get(self.report_datetime_field_attr):
            # falls within appointment's window period
            self.validate_crf_datetime_in_window_period(
                self.appointment,
                self.cleaned_data.get(self.report_datetime_field_attr),
                self.report_datetime_field_attr,
            )
            # falls within a valid consent period
            self.get_consent_for_period_or_raise(
                self.cleaned_data.get(self.report_datetime_field_attr)
            )
            # not before consent date
            if self.cleaned_data.get(self.report_datetime_field_attr) < self.consent_datetime:
                self.raise_validation_error(
                    {
                        self.report_datetime_field_attr: (
                            "Invalid. Cannot be before date of consent. "
                            "Participant consent on "
                            f"{formatted_datetime(self.consent_datetime)}"
                        )
                    }
                )

    @property
    def appointment(self) -> Appointment:
        try:
            return self.related_visit.appointment
        except AttributeError:
            self.raise_validation_error(
                f"{self.related_visit._meta.verbose_name} is required.", INVALID_ERROR
            )

    @property
    def subject_visit(self) -> VisitModelMixin:
        warnings.warn(
            "The subject_visit attribute is deprecated in favor of related_visit.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.related_visit

    @property
    def related_visit(self) -> VisitModelMixin:
        """Returns a subject visit model instance or None."""
        return get_related_visit(
            self, related_visit_model_attr=self.instance.related_visit_model_attr()
        )

    @property
    def subject_identifier(self) -> str:
        return self.appointment.subject_identifier

    @property
    def consent_datetime(self) -> datetime:
        return (
            get_registered_subject_model_cls()
            .objects.get(subject_identifier=self.subject_identifier)
            .consent_datetime
        )

    def validate_datetime_against_report_datetime(self, field: str) -> None:
        """Datetime cannot be after report_datetime"""
        if (
            self.cleaned_data.get(field)
            and self.cleaned_data.get(self.report_datetime_field_attr)
            and self.cleaned_data.get(field)
            > self.cleaned_data.get(self.report_datetime_field_attr)
        ):
            self.raise_validation_error(
                {field: "Cannot be after report datetime"}, INVALID_ERROR
            )

    def validate_date_against_report_datetime(self, field: str) -> None:
        """Date cannot be after report_datetime"""
        if (
            self.cleaned_data.get(field)
            and self.cleaned_data.get(self.report_datetime_field_attr)
            and self.cleaned_data.get(field)
            > self.cleaned_data.get(self.report_datetime_field_attr).date()
        ):
            self.raise_validation_error(
                {field: "Cannot be after report datetime"}, INVALID_ERROR
            )
