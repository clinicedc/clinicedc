from django.db.models import options
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from ..exceptions import NotConsentedError
from ..site_consents import site_consents, SiteConsentError

options.DEFAULT_NAMES = (options.DEFAULT_NAMES
                         + ('consent_model', 'consent_group'))


class RequiresConsentModelMixin(models.Model):

    """Requires a model to check for a valid consent before
    allowing to save.

    Requires attrs subject_identfier, report_datetime.
    """

    require_consent_on_change = True

    consent_version = models.CharField(
        max_length=10, default='?', editable=False)

    def save(self, *args, **kwargs):
        if not self._meta.consent_model:
            raise ImproperlyConfigured(
                'Consent model attribute not set. Got '
                f'\'{self._meta.label_lower}.consent_model\' = None')
        super().save(*args, **kwargs)

    def get_consent_object(self):
        consent_object = site_consents.get_consent(
            consent_model=self._meta.consent_model,
            consent_group=self._meta.consent_group,
            report_datetime=self.report_datetime)
        return consent_object

    def common_clean(self):
        if not self.id or (self.id and self.require_consent_on_change):
            consent_object = self.get_consent_object()
            self.consent_version = consent_object.version
            try:
                subject_identifier = self.appointment.subject_identifier
            except AttributeError:
                subject_identifier = self.subject_identifier
            try:
                if not subject_identifier:
                    raise SiteConsentError(
                        'Cannot lookup {} instance for subject. '
                        'Got \'subject_identifier\' is None.'.format(
                            consent_object.model._meta.label_lower))
                options = dict(
                    subject_identifier=subject_identifier,
                    version=consent_object.version)
                consent_object.model.objects.get(**options)
            except consent_object.model.DoesNotExist:
                raise NotConsentedError(
                    'Consent is required. Cannot find \'{consent_model} '
                    'version {version}\' when saving model \'{model}\' for '
                    'subject \'{subject_identifier}\' with date '
                    '\'{report_datetime}\' .'.format(
                        subject_identifier=subject_identifier,
                        consent_model=consent_object.model._meta.label_lower,
                        model=self._meta.label_lower,
                        version=consent_object.version,
                        report_datetime=self.report_datetime.strftime(
                            '%Y-%m-%d %H:%M%z')))
        super().common_clean()

    class Meta:
        abstract = True
        consent_model = None
        consent_group = None
