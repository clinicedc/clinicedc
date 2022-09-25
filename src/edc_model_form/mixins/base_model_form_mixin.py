from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from edc_registration import get_registered_subject_model_cls


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

    @property
    def subject_identifier(self) -> str:
        """Returns subject identifier.

        Assumes a non-CRF with model field subject_identifier.
        """
        if (
            subject_identifier := self.cleaned_data.get("subject_identifier")
            or self.instance.subject_identifier
        ):
            return subject_identifier
        else:
            raise ValidationError("Invalid. Subject identifier cannot be none.")

    @property
    def report_datetime(self) -> datetime:
        return self.cleaned_data.get(self.report_datetime_field_attr) or getattr(
            self.instance, self.report_datetime_field_attr
        )
