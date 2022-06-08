from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from edc_constants.constants import NO, YES
from edc_utils import AgeValueError, age, formatted_age

from ...site_consents import ConsentObjectDoesNotExist, SiteConsentError, site_consents
from ...utils import InvalidInitials, verify_initials_against_full_name


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
                    {
                        "dob": (
                            f"Subject's age is {self.age_delta.years}. "
                            "Subject is not eligible for consent. Minimum age of consent is "
                            f"{self.consent_config.age_min}."
                        )
                    }
                )

    def validate_max_age(self: Any) -> None:
        """Raises if age is above the age of consent"""
        if self.age_delta:
            if self.age_delta.years > self.consent_config.age_max:
                raise forms.ValidationError(
                    {
                        "dob": (
                            f"Subject's age is {self.age_delta.years}. "
                            "Subject is not eligible for consent. Maximum age of consent is "
                            f"{self.consent_config.age_max}."
                        )
                    }
                )

    def validate_identity_and_confirm_identity(self: Any) -> None:
        if self._identity and self._confirm_identity:
            if self._identity != self._confirm_identity:
                msg = (
                    "Identity mismatch. Identity must match "
                    f"the confirmation field. Got {self._identity} != "
                    f"{self._confirm_identity}"
                )
                if "identity" in self.cleaned_data:
                    raise forms.ValidationError({"identity": msg})
                else:
                    raise forms.ValidationError({"__all__": msg})

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
            msg = (
                "Identity number already submitted for consent "
                f"{self.consent_config.version}. "
                f"See `{subject_consent.subject_identifier}`."
            )
            if "identity" in self.cleaned_data:
                raise forms.ValidationError({"identity": msg})
            else:
                raise forms.ValidationError({"__all__": msg})

    def validate_identity_with_unique_fields(self: Any) -> None:
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        initials = cleaned_data.get("initials")
        dob = cleaned_data.get("dob")
        if (
            subject_consent := self._meta.model.objects.filter(
                first_name=first_name,
                initials=initials,
                dob=dob,
                version=self.consent_config.version,
            )
            .exclude(identity=self._identity)
            .last()
        ):
            raise forms.ValidationError(
                f"These personal details (first name, initials, dob) describe "
                f"another subject. See {subject_consent.subject_identifier} (1)."
            )

    def validate_initials_with_full_name(self: Any) -> None:
        cleaned_data = self.cleaned_data
        try:
            verify_initials_against_full_name(**cleaned_data)
        except InvalidInitials as e:
            raise forms.ValidationError({"initials": str(e)})

    def validate_gender_of_consent(self: Any) -> str:
        """Validates gender is a gender of consent."""
        gender = self.cleaned_data.get("gender")
        if gender not in self.consent_config.gender:
            raise forms.ValidationError(
                "Gender of consent can only be '%(gender_of_consent)s'. " "Got '%(gender)s'.",
                params={
                    "gender_of_consent": "' or '".join(self.consent_config.gender),
                    "gender": gender,
                },
                code="invalid",
            )
        return gender

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
                    {
                        "guardian_name": (
                            f"Subject's age is {formatted_age(dob, self._consent_datetime)}. "
                            "Subject is a minor. Guardian's "
                            "name is required with signature on the paper "
                            "document."
                        )
                    }
                )
        if rdelta.years >= self.consent_config.age_is_adult and guardian:
            if guardian:
                raise forms.ValidationError(
                    {
                        "guardian_name": (
                            f"Subject's age is {formatted_age(dob, self._consent_datetime)}. "
                            "Subject is an adult. Guardian's name is NOT required."
                        )
                    }
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
