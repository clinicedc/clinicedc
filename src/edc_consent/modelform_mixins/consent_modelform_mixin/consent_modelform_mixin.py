from typing import Any

from ...consent_helper import ConsentHelper
from ...site_consents import site_consents
from .clean_fields_modelform_mixin import CleanFieldsModelformMixin
from .custom_validation_mixin import CustomValidationMixin


class ConsentModelFormMixin(CleanFieldsModelformMixin, CustomValidationMixin):
    def clean(self: Any):
        cleaned_data = super().clean()  # noqa
        self.validate_initials_with_full_name()
        self.validate_gender_of_consent()
        self.validate_is_literate_and_witness()
        self.validate_dob_relative_to_consent_datetime()
        self.validate_guardian_and_dob()

        options = dict(
            consent_model=self._meta.model._meta.label_lower,
            consent_group=self._meta.model._meta.consent_group,
            report_datetime=self._consent_datetime,
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
