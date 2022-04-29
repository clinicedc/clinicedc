from datetime import datetime
from typing import Any

from edc_appointment.form_validators import WindowPeriodFormValidatorMixin
from edc_consent.form_validators import ConsentFormValidatorMixin
from edc_form_validators import FormValidator
from edc_registration.models import RegisteredSubject
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

    def validate_crf_report_datetime(self):
        if self.cleaned_data.get("report_datetime"):
            # falls within appointment's window period
            self.validate_crf_datetime_in_window_period(
                self.appointment,
                self.cleaned_data.get("report_datetime"),
                "report_datetime",
            )
            # falls within a valid consent period
            self.get_consent_for_period_or_raise(
                self.cleaned_data.get("report_datetime"), form_field="report_datetime"
            )
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
    def appointment(self) -> Any:
        return self.subject_visit.appointment

    @property
    def subject_visit(self) -> Any:
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
        return RegisteredSubject.objects.get(
            subject_identifier=self.subject_identifier
        ).consent_datetime
