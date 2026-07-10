from __future__ import annotations

from django import forms
from django.apps import apps as django_apps
from django.conf import settings

from edc_appointment.constants import MISSED_APPT
from edc_appointment.utils import get_appointment_model_cls
from edc_registration.models import RegisteredSubject

VISIT_WINDOW_DAYS = 7


class ResultUpdateForm(forms.Form):
    subject_identifier = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject identifier"}
        ),
    )
    screening_identifier = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Screening identifier"}
        ),
    )
    visit = forms.CharField(
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select a visit after entering the subject identifier.",
    )

    def __init__(self, *args: object, order_datetime: object = None, **kwargs: object) -> None:
        self.order_datetime = order_datetime
        super().__init__(*args, **kwargs)

    def clean_subject_identifier(self) -> str:
        value = self.cleaned_data.get("subject_identifier", "").strip()
        if value and not RegisteredSubject.objects.filter(subject_identifier=value).exists():
            raise forms.ValidationError("Subject identifier not found in RegisteredSubject.")
        return value

    def clean_screening_identifier(self) -> str:
        value = self.cleaned_data.get("screening_identifier", "").strip()
        if value and not RegisteredSubject.objects.filter(screening_identifier=value).exists():
            raise forms.ValidationError("Screening identifier not found in RegisteredSubject.")
        return value

    def clean(self) -> dict:
        cleaned_data = super().clean()
        subject_identifier = cleaned_data.get("subject_identifier", "")
        visit_value = cleaned_data.get("visit", "").strip()

        if not subject_identifier and visit_value:
            raise forms.ValidationError("Provide the subject identifier first.")

        visit_code = ""
        visit_code_sequence: int | None = None

        if subject_identifier and visit_value:
            visit_code, visit_code_sequence = self._parse_visit_value(visit_value)
            self._validate_visit(
                subject_identifier,
                visit_code,
                visit_code_sequence,
                self.order_datetime,
            )

        cleaned_data["visit_code"] = visit_code
        cleaned_data["visit_code_sequence"] = visit_code_sequence
        return cleaned_data

    @staticmethod
    def _parse_visit_value(value: str) -> tuple[str, int]:
        """Parse a visit value like '1000.0' into (visit_code, sequence)."""
        try:
            visit_code, seq_str = value.rsplit(".", 1)
            visit_code_sequence = int(seq_str)
        except (ValueError, AttributeError) as e:
            raise forms.ValidationError(f"Invalid visit selection: {value}") from e
        return visit_code, visit_code_sequence

    @staticmethod
    def _validate_visit(
        subject_identifier: str,
        visit_code: str,
        visit_code_sequence: int,
        order_datetime: object = None,
    ) -> None:
        # Validate against the appointment (the subject visit may not be
        # reported yet). The date window uses the subject visit report date
        # when reported, otherwise the appointment date.
        appointment_model = get_appointment_model_cls()
        try:
            appointment = appointment_model.objects.exclude(appt_timing=MISSED_APPT).get(
                subject_identifier=subject_identifier,
                visit_code=visit_code,
                visit_code_sequence=visit_code_sequence,
            )
        except appointment_model.DoesNotExist as e:
            raise forms.ValidationError(
                f"No appointment {visit_code}.{visit_code_sequence} found for "
                f"subject {subject_identifier} (excluding missed appointments)."
            ) from e

        subject_visit_model = django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
        subject_visit = subject_visit_model.objects.filter(
            subject_identifier=subject_identifier,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        ).first()
        reference_datetime = (
            subject_visit.report_datetime
            if subject_visit and subject_visit.report_datetime
            else appointment.appt_datetime
        )
        if order_datetime and reference_datetime:
            delta = abs((order_datetime - reference_datetime).days)
            if delta > VISIT_WINDOW_DAYS:
                raise forms.ValidationError(
                    f"Order date is {delta} days from the visit date "
                    f"({reference_datetime:%Y-%m-%d}). "
                    f"Must be within {VISIT_WINDOW_DAYS} days."
                )
