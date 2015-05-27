from ..classes import ConsentHelper


class RequiresConsentMixin(object):

    def requires_consent(self):
        """Users may override to return False to bypass consent checks for this model instance."""
        return True

    def is_consented_for_instance(self):
        """Confirms subject has a consent that covers data entry for this model."""
        if self.requires_consent():
            return ConsentHelper(self).is_consented_for_subject_instance()
        return True

    def get_versioned_field_names(self, consent_version_number):
        """Returns a list of field names under version control by version number.

        Users should override at the model class to return a list of field names for a given version_number."""
        return []

    def validate_versioned_fields(self, cleaned_data=None, exception_cls=None, **kwargs):
        """Raises and exception of fields do not validate.

        Validate fields under consent version control. If a field is not to be included for this
        consent version, an exception will be raised."""
        ConsentHelper(self).validate_versioned_fields()
