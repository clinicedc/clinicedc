from edc_screening.utils import is_eligible_or_raise

from .clean_fields_modelform_validation_mixin import CleanFieldsModelFormValidationMixin
from .consent_modelform_validation_mixin import ConsentModelFormValidationMixin

__all__ = ["ConsentModelFormMixin"]


class ConsentModelFormMixin(
    CleanFieldsModelFormValidationMixin, ConsentModelFormValidationMixin
):
    def clean(self) -> dict:
        cleaned_data = super().clean()
        self.validate_is_eligible_or_raise()
        self.validate_initials_with_full_name()
        self.validate_gender_of_consent()
        self.validate_is_literate_and_witness()
        self.validate_dob_relative_to_consent_datetime()
        self.validate_guardian_and_dob()
        self.validate_identity_and_confirm_identity()
        self.validate_identity_with_unique_fields()
        self.validate_identity_plus_version_is_unique()
        return cleaned_data

    def validate_is_eligible_or_raise(self) -> None:
        screening_identifier = self.get_field_or_raise(
            "screening_identifier", "Screening identifier is required."
        )
        is_eligible_or_raise(screening_identifier=screening_identifier)
