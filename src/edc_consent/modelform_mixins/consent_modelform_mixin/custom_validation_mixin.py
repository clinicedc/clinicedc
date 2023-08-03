from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from dateutil.relativedelta import relativedelta
from django import forms
from edc_constants.constants import NO, YES
from edc_model_form.utils import get_field_or_raise
from edc_utils import AgeValueError, age, formatted_age

from ...site_consents import ConsentObjectDoesNotExist, SiteConsentError, site_consents
from ...utils import InvalidInitials, verify_initials_against_full_name

if TYPE_CHECKING:
    from ...consent import Consent


class CustomValidationMixin:
    """Form for models that are a subclass of BaseConsent."""

    @property
    def consent_config(self) -> Consent:
        """Returns a consent_config instance or raises on
        missing data.
        """
        try:
            consent_config = site_consents.get_consent(
                report_datetime=self.consent_datetime,
                consent_model=self._meta.model._meta.label_lower,
                consent_group=self._meta.model._meta.consent_group,
            )
        except (ConsentObjectDoesNotExist, SiteConsentError) as e:
            raise forms.ValidationError(e)
        if not consent_config.version:
            raise forms.ValidationError("Unable to determine consent version")
        return consent_config

    def get_field_or_raise(self, name: str, msg: str) -> Any:
        return get_field_or_raise(
            name, msg, cleaned_data=self.cleaned_data, instance=self.instance
        )

    @property
    def consent_datetime(self) -> datetime:
        return self.get_field_or_raise("consent_datetime", "Consent date and time is required")

    @property
    def identity(self) -> str:
        return self.get_field_or_raise("identity", "Identity is required")

    @property
    def confirm_identity(self) -> str:
        return self.get_field_or_raise("confirm_identity", "Confirmed identity is required")

    @property
    def age_delta(self) -> relativedelta | None:
        dob = self.cleaned_data.get("dob")
        if self.consent_datetime and dob:
            try:
                return age(dob, self.consent_datetime)
            except AgeValueError as e:
                raise forms.ValidationError(str(e))
        return None

    def validate_min_age(self) -> None:
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

    def validate_max_age(self) -> None:
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

    def validate_identity_and_confirm_identity(self) -> None:
        if self.identity and self.confirm_identity:
            if self.identity != self.confirm_identity:
                msg = (
                    "Identity mismatch. Identity must match "
                    f"the confirmation field. Got {self.identity} != "
                    f"{self.confirm_identity}"
                )
                if "identity" in self.cleaned_data:
                    raise forms.ValidationError({"identity": msg})
                else:
                    raise forms.ValidationError({"__all__": msg})

    def validate_identity_plus_version_is_unique(self) -> None:
        """Enforce a unique constraint on personal identity number
        + consent version.

        Note: since version is not part of cleaned data, django form
        will not do the integrity check by default.
        """
        exclude_opts = dict(id=self.instance.id) if self.instance.id else {}
        if (
            subject_consent := self._meta.model.objects.filter(
                identity=self.identity, version=self.consent_config.version
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

    def validate_identity_with_unique_fields(self) -> None:
        cleaned_data = self.cleaned_data
        msg_word = None
        first_name = cleaned_data.get("first_name")
        initials = cleaned_data.get("initials")
        familiar_name = cleaned_data.get("familiar_name")
        dob = cleaned_data.get("dob")
        opts = dict(
            initials=initials,
            dob=dob,
            version=self.consent_config.version,
        )
        if familiar_name:
            opts.update(familiar_name=familiar_name)
            msg_word = "familiar name"
        elif first_name:
            opts.update(first_name=first_name)
            msg_word = "first name"
        if (
            subject_consent := self._meta.model.objects.filter(**opts)
            .exclude(identity=self.identity)
            .last()
        ):
            raise forms.ValidationError(
                f"These personal details ({msg_word}, initials, dob) describe "
                f"another subject. See {subject_consent.subject_identifier} (1)."
            )

    def validate_initials_with_full_name(self) -> None:
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
                "Gender of consent can only be '%(gender_of_consent)s'. Got '%(gender)s'.",
                params={
                    "gender_of_consent": "' or '".join(self.consent_config.gender),
                    "gender": gender,
                },
                code="invalid",
            )
        return gender

    def validate_guardian_and_dob(self) -> None:
        """Validates guardian is required if age is below age_is_adult
        from consent config.
        """
        cleaned_data = self.cleaned_data
        guardian = cleaned_data.get("guardian_name")
        dob = cleaned_data.get("dob")
        rdelta = relativedelta(self.consent_datetime.date(), dob)
        if rdelta.years < self.consent_config.age_is_adult:
            if not guardian:
                raise forms.ValidationError(
                    {
                        "guardian_name": (
                            f"Subject's age is {formatted_age(dob, self.consent_datetime)}. "
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
                            f"Subject's age is {formatted_age(dob, self.consent_datetime)}. "
                            "Subject is an adult. Guardian's name is NOT required."
                        )
                    }
                )

    def validate_dob_relative_to_consent_datetime(self) -> None:
        """Validates that the dob is within the bounds of MIN and
        MAX set on the model.
        """
        self.validate_min_age()
        self.validate_max_age()

    def validate_is_literate_and_witness(self) -> None:
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
