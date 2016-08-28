from uuid import uuid4

from django.db import models
from django_crypto_fields.fields import EncryptedTextField
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from simple_history.models import HistoricalRecords as AuditTrail

from edc_base.model.validators import datetime_not_future
from edc_base.utils import formatted_age, age
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_protocol.validators import datetime_not_before_study_start

from .choices import YES_NO_DECLINED_COPY
from .exceptions import ConsentVersionError, SiteConsentError, NotConsentedError
from .field_mixins import VerificationFieldsMixin
from .managers import ObjectConsentManager, ConsentManager
from .site_consents import site_consents


class RequiresConsentMixin(models.Model):

    """Requires a model to check for a valid consent before allowing to save."""

    consent_model = None  # format app_label.model_name

    consent_version = models.CharField(max_length=10, default='?', editable=False)

    def save(self, *args, **kwargs):
        if not self.consent_model:
            raise ImproperlyConfigured(
                'Consent model attribute not set. Got \'{}.consent_model\' = None'.format(self._meta.label_lower))
        self.consented_for_period_or_raise()
        super(RequiresConsentMixin, self).save(*args, **kwargs)

    def consented_for_period_or_raise(self, report_datetime=None, subject_identifier=None, exception_cls=None):
        exception_cls = exception_cls or NotConsentedError
        report_datetime = report_datetime or self.report_datetime
        get_consent_config = self.get_consent_config(report_datetime, exception_cls=exception_cls)
        self.consent_version = get_consent_config.version
        if not subject_identifier:
            try:
                subject_identifier = self.subject_identifier
            except AttributeError:
                subject_identifier = self.get_subject_identifier()
        if not subject_identifier:
            raise ImproperlyConfigured(
                'Attribute subject_identifier cannot be None. Either set it manually, via a property, or check method resolution '
                'order if model is declared with multiple mixins. The mixin that updates subject_identifier '
                'should be declared before RequiresConsentMixin.')
        try:
            get_consent_config.model.objects.get(
                subject_identifier=subject_identifier,
                version=get_consent_config.version)
        except get_consent_config.model.DoesNotExist:
            raise exception_cls(
                'Cannot find \'{consent_model} version {version}\' when saving model \'{model}\' '
                'for subject \'{subject_identifier}\' with date \'{report_datetime}\' .'.format(
                    subject_identifier=subject_identifier,
                    consent_model=get_consent_config.model._meta.label_lower,
                    model=self._meta.label_lower,
                    version=get_consent_config.version,
                    report_datetime=report_datetime.date().isoformat()))

    @classmethod
    def get_consent_config(cls, report_datetime, exception_cls=None):
        """Returns the consent config class that matches the report datetime and consent model."""
        return site_consents.get_by_datetime(
            cls.consent_model, report_datetime, exception_cls=exception_cls)

    class Meta:
        abstract = True


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
        consent = site_consents.get_by_consent_datetime(
            self.__class__, self.consent_datetime)
        self.version = consent.version
        if consent.updates_version:
            try:
                previous_consent = self.__class__.objects.get(
                    subject_identifier=self.subject_identifier,
                    identity=self.identity,
                    version__in=consent.updates_version,
                    **self.additional_filter_options())
                previous_consent.subject_identifier_as_pk = self.subject_identifier_as_pk
                previous_consent.subject_identifier_aka = self.subject_identifier_aka
            except self.__class__.DoesNotExist:
                raise ConsentVersionError(
                    'Previous consent with version {0} for this subject not found. Version {1} updates {0}.'
                    'Ensure all details match (identity, dob, first_name, last_name)'.format(
                        consent.updates_version, self.version))
        super(ConsentModelMixin, self).save(*args, **kwargs)

    def set_uuid_as_subject_identifier_if_none(self):
        if not self.subject_identifier_as_pk:
            self.subject_identifier_as_pk = str(uuid4())  # this will never change

    def is_known_consent_model_or_raise(self, consent_model=None, exception_cls=None):
        """Raises an exception if not listed in ConsentType."""
        consent_model = consent_model or self
        exception_cls = exception_cls or SiteConsentError
        consents = site_consents.get_by_model(model=consent_model)
        if not consents:
            models = [consent.model_class._meta.verbose_name for consent in consents]
            raise exception_cls(
                '\'{}.{}\' is not a known consent model. '
                'Valid consent models are [\'{}\']. See AppConfig.'.format(
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


class SpecimenConsentMixin(VerificationFieldsMixin, models.Model):

    """ A base class for a model completed by the user indicating whether a participant has agreed
    for specimens to be stored after study closure."""

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=timezone.now,
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
        abstract = True
