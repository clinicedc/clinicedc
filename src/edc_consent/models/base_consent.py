from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_crypto_fields.fields import LastnameField, EncryptedTextField

from edc_base.utils import formatted_age, age
from edc_subject.models import BaseSubject
from edc_base.model.validators import datetime_not_future, datetime_not_before_study_start, eligible_if_no
from edc_constants.choices import YES_NO

from .base_consent_history import BaseConsentHistory


# allow a settings attribute to override the unique constraint on the
# subject identifier
try:
    subject_identifier_is_unique = settings.SUBJECT_IDENTIFIER_UNIQUE_ON_CONSENT
except:
    subject_identifier_is_unique = True


class BaseConsent(BaseSubject):

    MAX_SUBJECTS = 0
    SUBJECT_TYPES = []
    GENDER_OF_CONSENT = []
    AGE_IS_ADULT = 18

    """ Consent models should be subclasses of this """

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
        db_index=True,
        unique=subject_identifier_is_unique,
    )

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

    consent_version_on_entry = models.IntegerField(
        editable=False,
        default=1,
        help_text='Version of subject\'s initial edc_consent.'
    )

    consent_version_recent = models.IntegerField(
        editable=False,
        default=1,
        help_text='Version of subject\'s most recent edc_consent.'
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

    def __str__(self):
        return "{0} {1} {2}".format(
            self.mask_unset_subject_identifier(),
            self.first_name.field_cryptor.mask(self.first_name),
            self.initials
        )

    def save(self, *args, **kwargs):
        self.validate_subject_type()
        self.validate_max_subjects()
        if self.confirm_identity:
            if self.identity != self.confirm_identity:
                raise ValueError(
                    'Attribute \'identity\' must match attribute \'confirm_identity\'. '
                    'Catch this error on the form'
                )
        if not self.id:
            self._save_new_consent(kwargs.get('using', None))
        super(BaseConsent, self).save(*args, **kwargs)

    @property
    def age_at_consent(self):
        """Returns a relativedelta."""
        return age(self.dob, self.consent_datetime)

    def formatted_age_at_consent(self):
        """Returns a string representation."""
        return formatted_age(self.dob, self.consent_datetime)

    @property
    def report_datetime(self):
        return self.consent_datetime

    def get_consent_history_model(self):
        """Returns the history model for this app.

        Users must override to return a model of base class BaseConsentHistory"""

        return None

    def update_consent_history(self, created, using):
        """
        Updates the edc_consent history model for this edc_consent instance if there is a edc_consent history model.
        """
        if self.get_consent_history_model():
            if not issubclass(self.get_consent_history_model(), BaseConsentHistory):
                raise ImproperlyConfigured('Expected a subclass of BaseConsentHistory.')
            self.get_consent_history_model().objects.update_consent_history(self, created, using)

    def delete_consent_history(self, app_label, model_name, pk, using):
        if self.get_consent_history_model():
            if not issubclass(self.get_consent_history_model(), BaseConsentHistory):
                raise ImproperlyConfigured('Expected a subclass of BaseConsentHistory.')
            self.get_consent_history_model().objects.delete_consent_history(app_label, model_name, pk, using)

    def validate_subject_type(self):
        """Validates the subject type is not blank and is listed in self.SUBJECT_TYPES."""
        if not self.subject_type:
            raise ValueError('Field subject_type may not be blank.')
        try:
            if self.subject_type.lower() not in [s.lower() for s in self.SUBJECT_TYPES]:
                raise ValueError(
                    'Expected field \'subject_type\' to be any of {0}. Got \'{1}\'.'.format(
                        self.SUBJECT_TYPES, self.subject_type))
        except AttributeError:
            pass

    def validate_max_subjects(self, exception_cls=None):
        """Validates the number of subjects will not exceed self.MAX_SUBJECTS for new instances."""
        exception_cls = exception_cls or ValueError
        if not self.id:
            count = self.__class__.objects.filter(subject_type=self.subject_type).count()
            if count + 1 > self.MAX_SUBJECTS:
                    raise exception_cls(
                        'Maximum number of subjects has been reached for subject_type {0}. '
                        'Got {1}/{2}.'.format(self.subject_type, count, self.MAX_SUBJECTS)
                    )

    class Meta:
        abstract = True
