from django.db import models

from ..exceptions import NotConsentedError
from ..models import ConsentType


class RequiresConsentMixin(models.Model):

    CONSENT_MODEL = None

    consent_version = models.CharField(max_length=10, default='?', editable=False)

    def save(self, *args, **kwargs):
        try:
            consent_type = self.consent_type(self.report_datetime)
            self.consent_version = consent_type.version
            self.CONSENT_MODEL.objects.get(
                subject_identifier=self.subject_identifier,
                version=self.consent_version)
        except self.CONSENT_MODEL.DoesNotExist:
            raise NotConsentedError(
                'Cannot find an entered consent \'{}\' for model \'{}\' using '
                'consent version \'{}\' and report date \'{}\'. '.format(
                    self.CONSENT_MODEL._meta.verbose_name,
                    self._meta.verbose_name,
                    self.consent_version,
                    self.report_datetime.isoformat()))
        super(RequiresConsentMixin, self).save(*args, **kwargs)

    def consent_type(self, report_datetime):
        """Returns the consent type that matches the report datetime and consent model."""
        return ConsentType.objects.get_by_report_datetime(self.CONSENT_MODEL, report_datetime)

    class Meta:
        abstract = True

#     def get_versioned_field_names(self, consent_version_number):
#         """Returns a list of field names under version control by version number.
#
#         Users should override at the model class to return a list of field names for a given version_number."""
#         return []
#
#     def validate_versioned_fields(self, cleaned_data=None, exception_cls=None, **kwargs):
#         """Raises and exception if fields do not validate.
#
#         Validate fields under consent version control. If a field is not to be included for this
#         consent version, an exception will be raised."""
#         ConsentHelper(self).validate_versioned_fields()
