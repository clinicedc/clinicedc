import re

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_crypto_fields.fields import LastnameField, EncryptedTextField
from django_crypto_crypto_fields.utils import mask_encrypted

from edc.core.bhp_common.utils import formatted_age
from edc_subject.models import BaseSubject
from edc_base.model.validators import datetime_not_future, datetime_not_before_study_start, eligible_if_no
from edc_constants.choices import YES_NO

from ..classes import ConsentedSubjectIdentifier
from ..exceptions import ConsentError

from .base_consent_history import BaseConsentHistory


# allow a settings attribute to override the unique constraint on the
# subject identifier
try:
    subject_identifier_is_unique = settings.SUBJECT_IDENTIFIER_UNIQUE_ON_CONSENT
except:
    subject_identifier_is_unique = True


class BaseConsent(BaseSubject):

    """ Consent models should be subclasses of this """

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
        db_index=True,
        unique=subject_identifier_is_unique,
    )

    site_code = models.CharField(
        verbose_name='Site',
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
            mask_encrypted(self.first_name),
            self.initials
        )

    def get_site_code(self):
        return self.site_code

    def save_new_consent(self, using=None, subject_identifier=None):
        """ Users may override this to compliment the default behavior for new instances.

        Must return a subject_identifier or None."""

        return subject_identifier

    def _save_new_consent(self, using=None, **kwargs):
        """ Creates or gets a subject identifier.

        ..note:: registered subject is updated/created on edc.subject signal.

        Also, calls user method :func:`save_new_consent`"""
        try:
            registered_subject = getattr(self, 'registered_subject')
        except AttributeError:
            registered_subject = None
        self.subject_identifier = self.save_new_consent(using=using, subject_identifier=self.subject_identifier)
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        dummy = self.subject_identifier
        # recall, if subject_identifier is not set, subject_identifier will be a uuid.
        if re_pk.match(self.subject_identifier):
            # test for user provided subject_identifier field method
            if self.get_user_provided_subject_identifier_attrname():
                self.subject_identifier = self._get_user_provided_subject_identifier()
                if not self.subject_identifier:
                    self.subject_identifier = dummy
            # try to get from registered_subject (was created  using signal in edc.subject)
            if re_pk.match(self.subject_identifier):
                if registered_subject:
                    if registered_subject.subject_identifier:
                        # check for  registered subject key and if it already has
                        # a subject_identifier (e.g for subjects re-consenting)
                        self.subject_identifier = self.registered_subject.subject_identifier
            # create a subject identifier, if not already done
            if re_pk.match(self.subject_identifier):
                consented_subject_identifier = ConsentedSubjectIdentifier(site_code=self.get_site_code(), using=using)
                self.subject_identifier = consented_subject_identifier.get_identifier(using=using)
        if not self.subject_identifier:
            self.subject_identifier = dummy
        if re_pk.match(self.subject_identifier):
            raise ConsentError(
                "Subject identifier not set after saving new edc_consent! Got {0}".format(self.subject_identifier)
            )

    def save(self, *args, **kwargs):
        if self.confirm_identity:
            if self.identity != self.confirm_identity:
                raise ValueError(
                    'Attribute \'identity\' must match attribute \'confirm_identity\'. Catch this error on the form'
                )
        self.insert_dummy_identifier()
        # if adding, call _save_new_consent()
        if not self.id:
            self._save_new_consent(kwargs.get('using', None))
        super(BaseConsent, self).save(*args, **kwargs)

    @property
    def registered_subject_options(self):
        """Returns a dictionary of RegisteredSubject attributes
        ({field, value}) to be used, for example, as the defaults
        kwarg RegisteredSubject.objects.get_or_create()."""
        options = {
            'study_site': self.study_site,
            'dob': self.dob,
            'is_dob_estimated': self.is_dob_estimated,
            'gender': self.gender,
            'initials': self.initials,
            'identity': self.identity,
            'identity_type': self.identity_type,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'subject_type': self.get_subject_type(),
        }
        if self.last_name:
            options.update({'registration_status': 'consented'})
        return options

    @property
    def age(self):
        return relativedelta(self.consent_datetime, self.dob).years

    def formatted_age_at_consent(self):
        return formatted_age(self.dob, self.consent_datetime)

    @classmethod
    def get_consent_update_model(self):
        raise TypeError(
            'The ConsentUpdateModel is required. Specify a class method '
            'get_consent_update_model() on the model to return the ConsentUpdateModel class.')

    def get_report_datetime(self):
        return self.consent_datetime

    def get_subject_type(self):
        raise ImproperlyConfigured(
            'Method must be overridden to return a subject_type. '
            'e.g. \'subject\', \'maternal\', \'infant\', etc')

    def bypass_for_edit_dispatched_as_item(self, using=None, update_fields=None):
        """Allow bypass only if doing edc_consent verification."""
        # requery myself
        obj = self.__class__.objects.using(using).get(pk=self.pk)
        # dont allow values in these fields to change if dispatched
        may_not_change_these_fields = []
        for k, v in obj.__dict__.items():
            if k not in ['is_verified_datetime', 'is_verified']:
                may_not_change_these_fields.append((k, v))
        for k, v in may_not_change_these_fields:
            if k[0] != '_':
                if getattr(self, k) != v:
                    return False
        return True

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

    class Meta:
        abstract = True
