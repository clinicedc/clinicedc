from uuid import uuid4

from django.db import models
from django_crypto_fields.fields import EncryptedTextField
from simple_history.models import HistoricalRecords as AuditTrail

from edc_base.model.validators import datetime_not_future, datetime_not_before_study_start
from edc_base.utils import formatted_age, age
from edc_consent.site_consent_types import site_consent_types

from .exceptions import ConsentVersionError, ConsentTypeError

from .models.fields.verification_fields_mixin import VerificationFieldsMixin
from .managers import ObjectConsentManager, ConsentManager


class ConsentModelMixin(VerificationFieldsMixin, models.Model):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
    )

    subject_identifier_as_pk = models.CharField(
        verbose_name="Subject Identifier as pk",
        max_length=50,
        default=None,
        editable=False,
    )

    subject_identifier_aka = models.CharField(
        verbose_name="Subject Identifier a.k.a",
        max_length=50,
        null=True,
        editable=False,
        help_text='track a previously allocated identifier.'
    )

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
    )

    version = models.CharField(
        verbose_name='Consent version',
        max_length=10,
        default='?',
        help_text='See \'Consent Type\' for consent versions by period.',
        editable=False,
    )

    study_site = models.CharField(max_length=15, null=True)

    sid = models.CharField(
        verbose_name="SID",
        max_length=15,
        null=True,
        blank=True,
        help_text='Used for randomization against a prepared rando-list.'
    )

    comment = EncryptedTextField(
        verbose_name="Comment",
        max_length=250,
        blank=True,
        null=True
    )

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False,
        help_text='see also edc.data manager.'
    )

    objects = ObjectConsentManager()

    consent = ConsentManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.subject_identifier_as_pk, )

    def save(self, *args, **kwargs):
        self.is_known_consent_model_or_raise()
        self.set_uuid_as_subject_identifier_if_none()
        if not self.id and not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk
        consent_type = site_consent_types.get_by_consent_datetime(
            self.__class__, self.consent_datetime)
        self.version = consent_type.version
        if consent_type.updates_version:
            try:
                previous_consent = self.__class__.objects.get(
                    subject_identifier=self.subject_identifier,
                    identity=self.identity,
                    version__in=consent_type.updates_version,
                    **self.additional_filter_options())
                previous_consent.subject_identifier_as_pk = self.subject_identifier_as_pk
                previous_consent.subject_identifier_aka = self.subject_identifier_aka
            except self.__class__.DoesNotExist:
                raise ConsentVersionError(
                    'Previous consent with version {0} for this subject not found. Version {1} updates {0}.'
                    'Ensure all details match (identity, dob, first_name, last_name)'.format(
                        consent_type.updates_version, self.version))
        super(ConsentModelMixin, self).save(*args, **kwargs)

    def set_uuid_as_subject_identifier_if_none(self):
        if not self.subject_identifier_as_pk:
            self.subject_identifier_as_pk = str(uuid4())  # this will never change

    def is_known_consent_model_or_raise(self, consent_model=None, exception_cls=None):
        """Raises an exception if not listed in ConsentType."""
        consent_model = consent_model or self
        exception_cls = exception_cls or ConsentTypeError
        consent_types = site_consent_types.get_by_model(model=consent_model)
        if not consent_types:
            models = [ct.model_class._meta.verbose_name for ct in consent_types]
            raise exception_cls(
                '\'{}.{}\' is not a known consent model. '
                'Valid consent models are [\'{}\']. See ConsentType and/or edc_configuration.'.format(
                    consent_model._meta.app_label,
                    consent_model._meta.model_name,
                    '\', \''.join(models)))

    @property
    def report_datetime(self):
        return self.consent_datetime

    def additional_filter_options(self):
        """Additional kwargs to filter the consent when looking for the previous consent."""
        return {}

    @property
    def age_at_consent(self):
        """Returns a relativedelta."""
        return age(self.dob, self.consent_datetime)

    def formatted_age_at_consent(self):
        """Returns a string representation."""
        return formatted_age(self.dob, self.consent_datetime)

    def get_registration_datetime(self):
        return self.consent_datetime

    class Meta:
        abstract = True
        get_latest_by = 'consent_datetime'
        unique_together = (('first_name', 'dob', 'initials', 'version'), )
        ordering = ('created', )
