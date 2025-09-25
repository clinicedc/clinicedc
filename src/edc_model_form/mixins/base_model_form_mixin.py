from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError

from edc_model_form.mixins.report_datetime_modelform_mixin import (
    ReportDatetimeModelFormMixin,
)
from edc_registration import get_registered_subject_model_cls


class BaseModelFormMixinError(Exception):
    pass


__all__ = ["BaseModelFormMixin", "BaseModelFormMixinError"]


class BaseModelFormMixin(ReportDatetimeModelFormMixin):
    """Base modelform mixin for edc forms.

    If this is a CRF, use together with the modelform mixin
    from edc-visit-tracking.
    """

    def clean(self) -> dict:
        cleaned_data = super().clean()
        if not self.report_datetime_field_attr:
            raise BaseModelFormMixinError(
                "Attribute `report_datetime_field_attr` Cannot be None. "
                f"See modelform for {self._meta.model}."
            )
        self.validate_subject_identifier()
        return cleaned_data

    def get_subject_identifier(self):
        """Returns subject identifier.

        Assumes a non-CRF with model field subject_identifier.
        """
        subject_identifier = None
        if "subject_identifier" in self.cleaned_data:
            subject_identifier = self.cleaned_data.get("subject_identifier")
        elif self.instance:
            subject_identifier = self.instance.subject_identifier
        if not subject_identifier:
            raise ValidationError("Invalid. Subject identifier cannot be none.")
        return subject_identifier

    def validate_subject_identifier(self) -> None:
        """Validates subject_identifier exists in RegisteredSubject"""
        try:
            get_registered_subject_model_cls().objects.get(
                subject_identifier=self.get_subject_identifier()
            )
        except ObjectDoesNotExist as e:
            raise ValidationError(
                {
                    "subject_identifier": (
                        "Invalid. Subject is not registered. "
                        f"Got {self.get_subject_identifier()}."
                    )
                }
            ) from e
