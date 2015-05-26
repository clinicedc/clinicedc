from django.apps import apps

from edc_base.model.models import BaseUuidModel
from edc_offstudy.exceptions import SubjectOffStudyError
try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    SyncMixin = type('SyncMixin', (object, ), {})

# if 'edc.device.dispatch' in settings.INSTALLED_APPS:
#     from edc.device.dispatch.models import BaseDispatchSyncUuidModel as BaseSyncUuidModel
# else:
#     from edc.device.sync.models import BaseSyncUuidModel

from ..classes import ConsentHelper


class BaseConsentedUuidModel(BaseUuidModel, SyncMixin):

    """Base model class for all models that collect data requiring edc_consent.

    This is not a edc_consent model base class. It is used by scheduled models
    with a key to a visit tracking model."""

    def is_consented_for_instance(self):
        """Confirms subject has a edc_consent that covers data entry for this model."""
        return self.get_consent_helper_cls()(self).is_consented_for_subject_instance()

    def get_versioned_field_names(self, version_number):
        """Returns a list of field names under version control by version number.

        Users should override at the model class to return a
        list of field names for a given version_number."""
        return []

    def get_consent_helper_cls(self):
        """Returns an instance of the default ConsentHelper."""
        return ConsentHelper

    def validate_versioned_fields(self, cleaned_data=None, exception_cls=None, **kwargs):
        """Validate fields under edc_consent version control to be set
        to the default value or not (None)."""
        return self.get_consent_helper_cls()(self).validate_versioned_fields()

    def get_requires_consent(self):
        """Users may override to return False to bypass edc_consent checks for this model instance."""
        return True

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if self.id:
            TimePointStatus = apps.get_model('data_manager', 'TimePointStatus')
            try:
                TimePointStatus.check_time_point_status(self.get_visit().appointment, using=using)
            except AttributeError:
                TimePointStatus.check_time_point_status(self.appointment, using=using)
        if 'is_off_study' in dir(self):
            if self.is_off_study():
                raise SubjectOffStudyError(
                    'Model cannot be saved. Subject is off study. Perhaps catch '
                    'this exception in forms clean() method.')
        super(BaseConsentedUuidModel, self).save(*args, **kwargs)

    def raw_save(self, *args, **kwargs):
        """For modifying models after subject is off study, mainly for data cleaning( for use backend)."""
        super(BaseConsentedUuidModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
