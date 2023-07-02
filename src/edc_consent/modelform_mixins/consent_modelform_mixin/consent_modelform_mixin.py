from edc_screening.utils import is_eligible_or_raise

from ...consent_helper import ConsentHelper
from ...site_consents import site_consents
from .clean_fields_modelform_mixin import CleanFieldsModelformMixin
from .custom_validation_mixin import CustomValidationMixin


class ConsentModelFormMixin(CleanFieldsModelformMixin, CustomValidationMixin):
    def clean(self) -> dict:
        cleaned_data = super().clean()
        self.validate_is_eligible_or_raise()
        self.validate_initials_with_full_name()
        self.validate_gender_of_consent()
        self.validate_is_literate_and_witness()
        self.validate_dob_relative_to_consent_datetime()
        self.validate_guardian_and_dob()

        options = dict(
            consent_model=self._meta.model._meta.label_lower,
            consent_group=self._meta.model._meta.consent_group,
            report_datetime=self.consent_datetime,
        )
        consent = site_consents.get_consent(**options)
        if consent.updates_versions:
            ConsentHelper(
                model_cls=self._meta.model,
                update_previous=False,
                **cleaned_data,
            )
        self.validate_identity_and_confirm_identity()
        self.validate_identity_with_unique_fields()
        self.validate_identity_plus_version_is_unique()
        return cleaned_data

    def validate_is_eligible_or_raise(self) -> None:
        screening_identifier = self.get_field_or_raise(
            "screening_identifier", "Screening identifier is required."
        )
        is_eligible_or_raise(screening_identifier=screening_identifier)
