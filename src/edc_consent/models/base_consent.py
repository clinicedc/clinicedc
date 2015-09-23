from uuid import uuid4

from django.db import models

from edc_consent.audit_trail import AuditTrail
from edc_consent.encrypted_fields import EncryptedTextField
from edc_consent.utils import formatted_age, age
from edc_consent.validators import datetime_not_future, datetime_not_before_study_start

from ..exceptions import ConsentVersionError

from .consent_type import ConsentType


class ObjectConsentManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentManager(models.Manager):

    def valid_consent_for_period(self, subject_identifier, report_datetime):
        consent = None
        try:
            consent_type = ConsentType.objects.get_by_consent_datetime(
                self.model, report_datetime)
            consent = self.get(subject_identifier=subject_identifier, version=consent_type.version)
        except (ConsentType.DoesNotExist, self.model.DoesNotExist):
            pass
        return consent


class BaseConsent(models.Model):

    MAX_SUBJECTS = 0

    get_latest_by = 'consent_datetime'

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
    )

    subject_identifier_as_pk = models.CharField(
        verbose_name="Subject Identifier as pk",
        max_length=50,
        default=uuid4
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

    is_verified = models.BooleanField(default=False, editable=False)

    is_verified_datetime = models.DateTimeField(null=True)

    version = models.CharField(max_length=10, default='?')

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
        if not self.id and not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk
        consent_type = ConsentType.objects.get_by_consent_datetime(
            self.__class__, self.consent_datetime)
        self.version = consent_type.version
        if consent_type.updates_version:
            try:
                previous_consent = self.__class__.objects.get(
                    subject_identifier=self.subject_identifier,
                    identity=self.identity,
                    version__in=consent_type.updates_version.split(','),
                    **self.additional_filter_options())
                previous_consent.subject_identifier_as_pk = self.subject_identifier_as_pk
                previous_consent.subject_identifier_aka = self.subject_identifier_aka
            except self.__class__.DoesNotExist:
                raise ConsentVersionError(
                    'Previous consent with version {0} for this subject not found. Version {1} updates {0}.'
                    'Ensure all details match (identity, dob, first_name, last_name)'.format(
                        consent_type.updates_version.split(','), self.version))
        super(BaseConsent, self).save(*args, **kwargs)

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

    class Meta:
        abstract = True
