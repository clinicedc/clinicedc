from datetime import datetime
from typing import Any

from django.apps import apps as django_apps
from edc_appointment.form_validators import WindowPeriodFormValidatorMixin
from edc_consent.form_validators import ConsentFormValidatorMixin
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_utils import formatted_datetime


class CrfFormValidator(
    WindowPeriodFormValidatorMixin, ConsentFormValidatorMixin, FormValidator
):
    """Form validator for CRfs.

    CRFs have a FK to subject_visit.
    """

    def _clean(self) -> None:
        self.validate_crf_report_datetime()
        super()._clean()

    def validate_crf_report_datetime(self: Any) -> None:
        if self.cleaned_data.get("report_datetime"):
            # falls within appointment's window period
            self.validate_crf_datetime_in_window_period(
                self.appointment,
                self.cleaned_data.get("report_datetime"),
                "report_datetime",
            )
            # falls within a valid consent period
            self.get_consent_for_period_or_raise(self.cleaned_data.get("report_datetime"))
            # not before consent date
            if self.cleaned_data.get("report_datetime") < self.consent_datetime:
                self.raise_validation_error(
                    {
                        "report_datetime": (
                            "Invalid. Cannot be before date of consent. "
                            "Participant consent on "
                            f"{formatted_datetime(self.consent_datetime)}"
                        )
                    }
                )

    @property
    def appointment(self: Any) -> Any:
        try:
            return self.subject_visit.appointment
        except AttributeError:
            self.raise_validation_error("Subject visit is required.", INVALID_ERROR)

    @property
    def subject_visit(self: Any) -> Any:
        """Returns a subject visit model instance or None"""
        try:
            subject_visit = self.instance.subject_visit
        except AttributeError:
            subject_visit = self.cleaned_data.get("subject_visit")
        return subject_visit

    @property
    def subject_identifier(self) -> str:
        return self.appointment.subject_identifier

    @property
    def consent_datetime(self) -> datetime:
        registered_subject_model_cls = django_apps.get_model(
            "edc_registration.registeredsubject"
        )
        return registered_subject_model_cls.objects.get(
            subject_identifier=self.subject_identifier
        ).consent_datetime

    def validate_datetime_against_report_datetime(self, field):
        """Datetime cannot be after report_datetime"""
        if (
            self.cleaned_data.get(field)
            and self.cleaned_data.get("report_datetime")
            and self.cleaned_data.get(field) > self.cleaned_data.get("report_datetime")
        ):
            self.raise_validation_error(
                {field: "Cannot to after report datetime"}, INVALID_ERROR
            )

    def validate_date_against_report_datetime(self, field):
        """Date cannot be after report_datetime"""
        if (
            self.cleaned_data.get(field)
            and self.cleaned_data.get("report_datetime")
            and self.cleaned_data.get(field) > self.cleaned_data.get("report_datetime").date()
        ):
            self.raise_validation_error(
                {field: "Cannot to after report datetime"}, INVALID_ERROR
            )
