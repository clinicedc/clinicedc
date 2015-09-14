# from edc_appointment.models import TimePointStatus
# from edc_base.model.models import BaseUuidModel
# try:
#     from edc_sync.mixins import SyncMixin
# except ImportError:
#     SyncMixin = type('SyncMixin', (object, ), {})
#
#
# class BaseConsentedUuidModel(BaseUuidModel, SyncMixin):
#
#    """Base model class for all models that collect data requiring edc_consent.
#
#    This is not a edc_consent model base class. It is used by scheduled models
#    with a key to a visit tracking model."""
#
#    def get_versioned_field_names(self, version_number):
#        """Returns a list of field names under version control by version number.
#
#        Users should override at the model class to return a
#        list of field names for a given version_number."""
#        return []
#
#    def validate_versioned_fields(self, cleaned_data=None, exception_cls=None, **kwargs):
#        """Validate fields under edc_consent version control to be set
#        to the default value or not (None)."""
#        return self.get_consent_helper_cls()(self).validate_versioned_fields()
#
#    def save(self, *args, **kwargs):
#        using = kwargs.get('using')
#        if self.id:
#            try:
#                TimePointStatus.check_time_point_status(self.get_visit().appointment, using=using)
#            except AttributeError:
#                TimePointStatus.check_time_point_status(self.appointment, using=using)
#        if 'is_off_study' in dir(self):
#            if self.is_off_study():
#                raise ValueError(
#                    'Model cannot be saved. Subject is off study. Perhaps catch '
#                    'this exception in forms clean() method.')
#        super(BaseConsentedUuidModel, self).save(*args, **kwargs)
#
#    class Meta:
#        abstract = True
