from uuid import uuid4

from django.db.models import options
from django.db import models
from django_crypto_fields.fields import EncryptedTextField
from django.core.exceptions import ImproperlyConfigured, MultipleObjectsReturned

from edc_base.model.validators import datetime_not_future
from edc_base.utils import formatted_age, age, get_utcnow
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_protocol.validators import datetime_not_before_study_start

from .choices import YES_NO_DECLINED_COPY
from .exceptions import SiteConsentError, NotConsentedError, ConsentVersionSequenceError
from .field_mixins import VerificationFieldsMixin
from .managers import ObjectConsentManager, ConsentManager
from .site_consents import site_consents
from edc_consent.exceptions import ConsentDoesNotExist


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model', 'consent_group')


class RequiresConsentMixin(models.Model):

    """Requires a model to check for a valid consent before allowing to save.

    Requires attrs subject_identfier, report_datetime"""

    consent_version = models.CharField(max_length=10, default='?', editable=False)

    def save(self, *args, **kwargs):
        if not self._meta.consent_model:
            raise ImproperlyConfigured(
                'Consent model attribute not set. Got \'{}.consent_model\' = None'.format(
                    self._meta.label_lower))
        super(RequiresConsentMixin, self).save(*args, **kwargs)

    def get_consent_object(self):
        consent_object = site_consents.get_consent(
            consent_model=self._meta.consent_model,
            consent_group=self._meta.consent_group,
            report_datetime=self.report_datetime)
        return consent_object

    def common_clean(self):
        consent_object = self.get_consent_object()
        self.consent_version = consent_object.version
        try:
            if not self.subject_identifier:
                raise SiteConsentError(
                    'Cannot lookup {} instance for subject. Got \'subject_identifier\' is None.'.format(
                        consent_object.model._meta.label_lower))
            options = dict(
                subject_identifier=self.subject_identifier,
                version=consent_object.version)
            consent_object.model.objects.get(**options)
        except consent_object.model.DoesNotExist:
            raise NotConsentedError(
                'Consent is required. Cannot find \'{consent_model} version {version}\' '
                'when saving model \'{model}\' for subject \'{subject_identifier}\' with date '
                '\'{report_datetime}\' .'.format(
                    subject_identifier=self.subject_identifier,
                    consent_model=consent_object.model._meta.label_lower,
                    model=self._meta.label_lower,
                    version=consent_object.version,
                    report_datetime=self.report_datetime.strftime('%Y-%m-%d %H:%M%z')))
        super().common_clean()

    class Meta:
        abstract = True
        consent_model = None
        consent_group = None


class ConsentModelMixin(VerificationFieldsMixin, models.Model):

    """Mixin for a Consent model class such as SubjectConsent.

    Use with edc_identifier's SubjectIdentifierModelMixin"""

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

    consent_identifier = models.UUIDField(
        default=uuid4,
        editable=False,
        help_text='A unique identifier for this consent instance')

    objects = ObjectConsentManager()

    consent = ConsentManager()

    def __str__(self):
        return '{0} {1} {2} ({3}) v{4}'.format(
            self.subject_identifier, self.first_name, self.last_name, self.initials, self.version)

    def natural_key(self):
        return (self.subject_identifier_as_pk, )

    def save(self, *args, **kwargs):
        consent = site_consents.get_consent(
            consent_model=self._meta.label_lower,
            consent_group=self._meta.consent_group,
            report_datetime=self.consent_datetime)
        self.version = consent.version
        if consent.updates_versions:
            previous_consent = self.previous_consent_to_update(consent)
            previous_consent.subject_identifier_as_pk = self.subject_identifier_as_pk
            previous_consent.subject_identifier_aka = self.subject_identifier_aka
        super(ConsentModelMixin, self).save(*args, **kwargs)

    def previous_consent_to_update(self, consent):
        previous_consent = None
        try:
            previous_consent = self.__class__.objects.get(
                subject_identifier=self.subject_identifier,
                identity=self.identity,
                version__in=consent.updates_versions,
                **self.additional_filter_options())
        except self.__class__.DoesNotExist:
            raise ConsentVersionSequenceError(
                'Previous consent with version {0} for this subject not found. Version {1} updates {0}. '
                'Ensure all details match (identity, dob, first_name, last_name)'.format(
                    ', '.join(consent.updates_versions), self.version))
        except MultipleObjectsReturned:
            previous_consents = self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                identity=self.identity,
                version__in=consent.updates_versions,
                **self.additional_filter_options()).order_by('-version')
            previous_consent = previous_consents[0]
        return previous_consent

    @property
    def common_clean_exceptions(self):
        common_clean_exceptions = super().common_clean_exceptions
        return common_clean_exceptions + [ConsentVersionSequenceError, ConsentDoesNotExist]

    def common_clean(self):
        consent = site_consents.get_consent(
            consent_model=self._meta.label_lower,
            consent_group=self._meta.consent_group,
            report_datetime=self.consent_datetime)
        if consent.updates_versions:
            self.previous_consent_to_update(consent)
        super().common_clean()

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
        consent_group = None
        get_latest_by = 'consent_datetime'
        unique_together = (('first_name', 'dob', 'initials', 'version'), )
        ordering = ('created', )


class SpecimenConsentMixin(VerificationFieldsMixin, models.Model):

    """ A base class for a model completed by the user indicating whether a participant has agreed
    for specimens to be stored after study closure."""

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=get_utcnow,
        help_text=('If reporting today, use today\'s date/time, otherwise use '
                   'the date/time this information was reported.'))

    version = models.CharField(
        verbose_name='Consent version',
        max_length=10,
        default='?',
        help_text='See \'Consent Type\' for consent versions by period.',
        editable=False,
    )

    purpose_explained = models.CharField(
        verbose_name=("I have explained the purpose of the specimen consent"
                      " to the participant."),
        max_length=15,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="")

    purpose_understood = models.CharField(
        verbose_name=("To the best of my knowledge, the client understands"
                      " the purpose, procedures, risks and benefits of the specimen consent"),
        max_length=15,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,)

    offered_copy = models.CharField(
        verbose_name=("I offered the participant a copy of the signed specimen consent and "
                      "the participant accepted the copy"),
        max_length=20,
        choices=YES_NO_DECLINED_COPY,
        null=True,
        blank=False,
        help_text=("If participant declined the copy, return the copy to the clinic to be "
                   "filed with the original specimen consent")
    )

    class Meta:
        consent_model = None
        consent_group = None
        abstract = True
