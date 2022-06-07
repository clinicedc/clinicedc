from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from edc_constants.constants import NO, YES
from edc_utils import AgeValueError, age, formatted_age

from ...site_consents import ConsentObjectDoesNotExist, SiteConsentError, site_consents
from ...utils import (
    InvalidInitials,
    values_as_string,
    verify_initials_against_full_name,
)


class CustomValidationMixin:
    """Form for models that are a subclass of BaseConsent."""

    @property
    def consent_config(self: Any) -> Any:
        """Returns a consent_config instance or raises on
        missing data.
        """
        try:
            consent_config = site_consents.get_consent(
                report_datetime=self._consent_datetime,
                consent_model=self._meta.model._meta.label_lower,
                consent_group=self._meta.model._meta.consent_group,
            )
        except (ConsentObjectDoesNotExist, SiteConsentError) as e:
            raise forms.ValidationError(e)
        if not consent_config.version:
            raise forms.ValidationError("Unable to determine consent version")
        return consent_config

    def get_field_or_raise(self: Any, name: str, msg: str) -> Any:
        """Returns a field value from cleaned_data if the key
        exists, or from the model instance.
        """
        if name in self.cleaned_data and not self.cleaned_data.get(name):
            raise forms.ValidationError({"__all__": msg})
        value = self.cleaned_data.get(name, getattr(self.instance, name))
        if not value:
            raise forms.ValidationError({"__all__": msg})
        return value

    @property
    def _consent_datetime(self: Any) -> Optional[datetime]:
        consent_datetime = self.get_field_or_raise(
            "consent_datetime", "Consent date and time is required"
        )
        return consent_datetime.astimezone(ZoneInfo(settings.TIME_ZONE))

    @property
    def _identity(self: Any) -> Optional[str]:
        return self.get_field_or_raise("identity", "Identity is required")

    @property
    def _confirm_identity(self: Any) -> Optional[str]:
        return self.get_field_or_raise("confirm_identity", "Confirmed identity is required")

    @property
    def age_delta(self: Any) -> Optional[relativedelta]:
        dob = self.cleaned_data.get("dob")
        if self._consent_datetime and dob:
            try:
                return age(dob, self._consent_datetime)
            except AgeValueError as e:
                raise forms.ValidationError(str(e))
        return None

    def validate_min_age(self: Any) -> None:
        """Raises if age is below the age of consent"""
        if self.age_delta:
            if self.age_delta.years < self.consent_config.age_min:
                raise forms.ValidationError(
                    "Subject's age is %(age)s. Subject is not eligible for "
                    "consent. Minimum age of consent is %(min)s.",
                    params={"age": self.age_delta.years, "min": self.consent_config.age_min},
                    code="invalid",
                )

    def validate_max_age(self: Any) -> None:
        """Raises if age is above the age of consent"""
        if self.age_delta:
            if self.age_delta.years > self.consent_config.age_max:
                raise forms.ValidationError(
                    "Subject's age is %(age)s. Subject is not eligible for "
                    "consent. Maximum age of consent is %(max)s.",
                    params={"age": self.age_delta.years, "max": self.consent_config.age_max},
                    code="invalid",
                )

    def validate_identity_and_confirm_identity(self: Any) -> None:
        if self._identity and self._confirm_identity:
            if self._identity != self._confirm_identity:
                raise forms.ValidationError(
                    {
                        "identity": "Identity mismatch. Identity must match "
                        f"the confirmation field. Got {self._identity} != "
                        f"{self._confirm_identity}"
                    }
                )

    def validate_identity_plus_version_is_unique(self: Any) -> None:  # noqa
        """Enforce a unique constraint on personal identity number
        + consent version.

        Note: since version is not part of cleaned data, django form
        will not do the integrity check by default.
        """
        exclude_opts = dict(id=self.instance.id) if self.instance.id else {}
        if (
            subject_consent := self._meta.model.objects.filter(
                identity=self._identity, version=self.consent_config.version
            )
            .exclude(**exclude_opts)
            .last()
        ):
            raise forms.ValidationError(
                {
                    "identity": (
                        "Identity number already submitted for consent "
                        f"{self.consent_config.version}. "
                        f"See `{subject_consent.subject_identifier}`."
                    ),
                },
            )

    def validate_identity_with_unique_fields(self: Any) -> None:
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        initials = cleaned_data.get("initials")
        dob = cleaned_data.get("dob")
        unique_together_on_form = values_as_string(
            first_name, initials, dob, self.consent_config.version
        )
        if unique_together_on_form:
            for subject_consent in self._meta.model.objects.filter(identity=self._identity):
                unique_together_on_model = values_as_string(
                    subject_consent.first_name,
                    subject_consent.initials,
                    subject_consent.dob,
                    subject_consent.version,
                )
                if unique_together_on_form != unique_together_on_model:
                    raise forms.ValidationError(
                        {
                            "identity": (
                                f"Identity '{self._identity}' is already in use by "
                                f"another subject. See {subject_consent.subject_identifier}."
                            )
                        }
                    )
            for consent in self._meta.model.objects.filter(
                first_name=first_name, initials=initials, dob=dob
            ):
                if consent.identity != self._identity:
                    raise forms.ValidationError(
                        {
                            "identity": "Subject's identity was previously reported "
                            f"as '{consent.identity}'."
                        }
                    )

    def validate_initials_with_full_name(self: Any) -> None:
        cleaned_data = self.cleaned_data
        try:
            verify_initials_against_full_name(**cleaned_data)
        except InvalidInitials as e:
            raise forms.ValidationError({"initials": str(e)})

    def validate_guardian_and_dob(self: Any) -> None:
        """Validates guardian is required if age is below age_is_adult
        from consent config.
        """
        cleaned_data = self.cleaned_data
        guardian = cleaned_data.get("guardian_name")
        dob = cleaned_data.get("dob")
        rdelta = relativedelta(self._consent_datetime.date(), dob)
        if rdelta.years < self.consent_config.age_is_adult:
            if not guardian:
                raise forms.ValidationError(
                    "Subject's age is {}. Subject is a minor. Guardian's "
                    "name is required with signature on the paper "
                    "document.".format(formatted_age(dob, self._consent_datetime)),
                    params={"age": formatted_age(dob, self._consent_datetime)},
                    code="invalid",
                )
        if rdelta.years >= self.consent_config.age_is_adult and guardian:
            if guardian:
                raise forms.ValidationError(
                    "Subject's age is {}. Subject is an adult. Guardian's "
                    "name is NOT required.".format(formatted_age(dob, self._consent_datetime)),
                    params={"age": formatted_age(dob, self._consent_datetime)},
                    code="invalid",
                )

    def validate_dob_relative_to_consent_datetime(self: Any) -> None:
        """Validates that the dob is within the bounds of MIN and
        MAX set on the model.
        """
        self.validate_min_age()
        self.validate_max_age()

    def validate_is_literate_and_witness(self: Any) -> None:
        cleaned_data = self.cleaned_data
        is_literate = cleaned_data.get("is_literate")
        witness_name = cleaned_data.get("witness_name")
        if is_literate == NO and not witness_name:
            raise forms.ValidationError(
                {
                    "witness_name": "Provide a name of a witness on this form and "
                    "ensure paper consent is signed."
                }
            )
        if is_literate == YES and witness_name:
            raise forms.ValidationError({"witness_name": "This field is not required"})
