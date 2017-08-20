from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext as _

from django_crypto_fields.fields import FirstnameField, LastnameField
from django_crypto_fields.fields import IdentityField, EncryptedCharField

from edc_base.model_fields import IdentityTypeField, IsDateEstimatedField
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_uuid

from edc_constants.choices import GENDER
from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin

from ..model_mixins import UpdatesOrCreatesRegistrationModelMixin

from edc_base.model_mixins import DEFAULT_BASE_FIELDS


class SubjectEligibility(UniqueSubjectIdentifierModelMixin, UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):

    screening_identifier = models.CharField(
        max_length=36,
        null=True,
        unique=True)

    study_site = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    def update_subject_identifier_on_save(self):
        """Overridden to not set the subject identifier on save.
        """
        if not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk.hex
            self.subject_identifier_aka = self.subject_identifier_as_pk.hex
        return self.subject_identifier

    @property
    def registration_unique_field(self):
        return 'screening_identifier'


class SubjectConsent(UniqueSubjectIdentifierModelMixin, UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):

    first_name = FirstnameField(
        null=True)

    last_name = LastnameField(
        verbose_name="Last name",
        null=True)

    initials = EncryptedCharField(
        validators=[RegexValidator(
            regex=r'^[A-Z]{2,3}$',
            message=('Ensure initials consist of letters '
                     'only in upper case, no spaces.'))],
        null=True)

    dob = models.DateField(
        verbose_name=_("Date of birth"),
        null=True,
        blank=False,
        help_text=_("Format is YYYY-MM-DD"))

    is_dob_estimated = IsDateEstimatedField(
        verbose_name=_("Is date of birth estimated?"),
        null=True,
        blank=False)

    gender = models.CharField(
        verbose_name="Gender",
        max_length=1,
        choices=GENDER,
        null=True,
        blank=False)

    subject_consent_id = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    sid = models.CharField(
        verbose_name="SID",
        max_length=15,
        null=True,
        blank=True)

    study_site = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    subject_type = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    relative_identifier = models.CharField(
        verbose_name="Identifier of immediate relation",
        max_length=36,
        null=True,
        blank=True,
        help_text="For example, mother's identifier, if available / appropriate")

    identity = IdentityField(
        null=True,
        blank=True)

    identity_or_pk = models.CharField(
        verbose_name="identity or pk",
        max_length=75,
        unique=True,
        default=get_uuid,
        editable=False,
    )

    identity_type = IdentityTypeField(
        null=True,
        blank=True)

    screening_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True)

    @property
    def registration_unique_field(self):
        return 'screening_identifier'

    @property
    def registration_options(self):
        """Gathers values for common attributes between the
        registration model and this instance.
        """
        registration_options = {}
        rs = self.registration_model()
        for k, v in self.__dict__.items():
            if k not in DEFAULT_BASE_FIELDS + ['_state', 'subject_identifier_as_pk']:
                try:
                    getattr(rs, k)
                    registration_options.update({k: v})
                except AttributeError:
                    pass
        return registration_options
