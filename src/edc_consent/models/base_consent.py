from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_crypto_fields.fields import LastnameField, EncryptedTextField

from edc_base.utils import formatted_age, age
from edc_base.model.validators import datetime_not_future, datetime_not_before_study_start, eligible_if_no
from edc_constants.choices import YES_NO

from ..mixins.bw.identity_fields_mixin import IdentityFieldsMixin

from .subject import Subject
from .consent_type import ConsentType
from edc_consent.exceptions import ConsentVersionError


class BaseConsent(IdentityFieldsMixin, Subject):

    MAX_SUBJECTS = 0
    SUBJECT_TYPES = []
    GENDER_OF_CONSENT = []
    AGE_IS_ADULT = 18
    MINIMUM_AGE_OF_CONSENT = 16
    MAXIMUM_AGE_OF_CONSENT = 64

    """ Consent models should be subclasses of this """

    get_latest_by = 'consent_datetime'

    sid = models.CharField(
        verbose_name="SID",
        max_length=15,
        null=True,
        blank=True,
        help_text='Used for randomization against a prepared rando-list.'
    )

    site_code = models.CharField(
        verbose_name='Site',
        max_length=25,
        help_text="This refers to the site or 'clinic area' where the subject is being consented."
    )

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
    )

    guardian_name = LastnameField(
        verbose_name=("Guardian\'s Last and first name (minors only)"),
        validators=[
            RegexValidator(
                '^[A-Z]{1,50}\, [A-Z]{1,50}$',
                'Invalid format. Format is \'LASTNAME, FIRSTNAME\'. All uppercase separated by a comma')],
        blank=True,
        null=True,
        help_text=(
            'Required only if subject is a minor. Format is \'LASTNAME, FIRSTNAME\'. '
            'All uppercase separated by a comma then followe by a space.'),
    )

    may_store_samples = models.CharField(
        verbose_name=_("Sample storage"),
        max_length=3,
        choices=YES_NO,
        help_text=("Does the subject agree to have samples stored after the study has ended")
    )

    is_incarcerated = models.CharField(
        verbose_name="Is the participant under involuntary incarceration?",
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_no, ],
        default='-',
        help_text="( if 'YES' STOP patient cannot be consented )",
    )

    is_literate = models.CharField(
        verbose_name="Is the participant LITERATE?",
        max_length=3,
        choices=YES_NO,
        default='-',
        help_text="( if 'No' provide witness\'s name here and with signature on the paper document.)",
    )

    witness_name = LastnameField(
        verbose_name=_("Witness\'s Last and first name (illiterates only)"),
        validators=[
            RegexValidator(
                '^[A-Z]{1,50}\, [A-Z]{1,50}$',
                'Invalid format. Format is \'LASTNAME, FIRSTNAME\'. All uppercase separated by a comma')],
        blank=True,
        null=True,
        help_text=_(
            'Required only if subject is illiterate. Format is \'LASTNAME, FIRSTNAME\'. '
            'All uppercase separated by a comma'),
    )

    comment = EncryptedTextField(
        verbose_name="Comment",
        max_length=250,
        blank=True,
        null=True
    )

    language = models.CharField(
        verbose_name='Language of edc_consent',
        max_length=25,
        choices=settings.LANGUAGES,
        default='not specified',
        help_text='The language used for the edc_consent process will also be used during data collection.'
    )

    is_verified = models.BooleanField(default=False, editable=False)

    is_verified_datetime = models.DateTimeField(null=True)

    version = models.CharField(max_length=10)

    def __str__(self):
        return "{0} {1} {2} v{3}".format(
            self.mask_unset_subject_identifier(),
            self.first_name.field_cryptor.mask(self.first_name),
            self.initials,
            self.version
        )

    def save(self, *args, **kwargs):
        consent_type = ConsentType.objects.get_by_consent_datetime(
            self.__class__, self.consent_datetime)
        self.version = consent_type.version
        if consent_type.updates_version:
            try:
                previous_consent = self.__class__.objects.get(
                    subject_identifier=self.subject_identifier,
                    identity=self.identity,
                    dob=self.dob,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    version=consent_type.updates_version)
                previous_consent.subject_identifier_as_pk = self.subject_identifier_as_pk
                previous_consent.subject_identifier_aka = self.subject_identifier_aka
            except self.__class__.DoesNotExist:
                raise ConsentVersionError(
                    'Previous consent with version {0} for this subject not found. Version {1} updates {0}.'
                    'Ensure all details match (identity, dob, first_name, last_name)'.format(
                        consent_type.updates_version, self.version))
        super(BaseConsent, self).save(*args, **kwargs)

    @property
    def age_at_consent(self):
        """Returns a relativedelta."""
        return age(self.dob, self.consent_datetime)

    def formatted_age_at_consent(self):
        """Returns a string representation."""
        return formatted_age(self.dob, self.consent_datetime)

    class Meta(Subject.Meta):
        abstract = True
