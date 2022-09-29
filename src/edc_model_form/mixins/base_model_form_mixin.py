from __future__ import annotations

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from edc_registration import get_registered_subject_model_cls
from edc_utils import to_utc


class BaseModelFormMixinError(Exception):
    pass


class BaseModelFormMixin:

    """Base modeform mixin for edc forms.

    If this is a CRF, use together with the modelform mixin
    from edc-visit-tracking.
    """

    # may also be appt_datetime or requisition_datetime
    report_datetime_field_attr: str = None

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if not self.report_datetime_field_attr:
            raise BaseModelFormMixinError(
                "Attribute `report_datetime_field_attr` Cannot be None. "
                f"See modeform for {self._meta.model}."
            )
        self.validate_subject_identifier()
        return cleaned_data

    @property
    def subject_identifier(self) -> str:
        """Returns subject identifier.

        Assumes a non-CRF with model field subject_identifier.
        """
        if "subject_identifier" in self.cleaned_data:
            subject_identifier = self.cleaned_data.get("subject_identifier")
        else:
            subject_identifier = self.instance.subject_identifier
        if not subject_identifier:
            raise ValidationError("Invalid. Subject identifier cannot be none.")
        return subject_identifier

    @property
    def report_datetime(self) -> datetime | None:
        """Returns the report_datetime in UTC from cleaned_data,
        if key exists, else returns the instance report_datetime.
        """
        if self.report_datetime_field_attr in self.cleaned_data:
            return to_utc(self.cleaned_data.get(self.report_datetime_field_attr))
        else:
            return getattr(self.instance, self.report_datetime_field_attr)

    def validate_subject_identifier(self) -> None:
        """Validates subject_identifier exists in RegisteredSubject"""
        try:
            get_registered_subject_model_cls().objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            raise ValidationError(
                {
                    "subject_identifier": (
                        f"Invalid. Subject is not registered. Got {self.subject_identifier}."
                    )
                }
            )
