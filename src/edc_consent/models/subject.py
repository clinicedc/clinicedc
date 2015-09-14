from uuid import uuid4

from edc_base.model.models import BaseUuidModel

from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models
from django_crypto_fields.fields import FirstnameField, LastnameField, EncryptedCharField

from edc_base.model.fields import IsDateEstimatedField
from edc_base.model.validators import dob_not_future, MinConsentAgeValidator, MaxConsentAgeValidator
from edc_constants.choices import GENDER_UNDETERMINED

from .validators import SubjectTypeValidator

# allow a settings attribute to override the unique constraint on the
# subject identifier
try:
    subject_identifier_is_unique = settings.SUBJECT_IDENTIFIER_UNIQUE_ON_CONSENT
except AttributeError:
    subject_identifier_is_unique = True


class SubjectManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class Subject (BaseUuidModel):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
    )

    subject_identifier_as_pk = models.UUIDField(
        verbose_name="Subject Identifier as pk",
        default=uuid4
    )

    subject_identifier_aka = models.CharField(
        verbose_name="Subject Identifier a.k.a",
        max_length=50,
        null=True,
        editable=False,
        help_text='track a previously allocated identifier.'
    )

    # may not be available when instance created (e.g. infants prior to birth report)
    first_name = FirstnameField(
        null=True,
    )

    # may not be available when instance created (e.g. infants or household subject before consent)
    last_name = LastnameField(
        verbose_name="Last name",
        null=True,
    )

    # may not be available when instance created (e.g. infants)
    initials = EncryptedCharField(
        validators=[RegexValidator(regex=r'^[A-Z]{2,3}$',
                                   message=('Ensure initials consist of letters '
                                            'only in upper case, no spaces.')), ],
        null=True,
    )

    dob = models.DateField(
        verbose_name="Date of birth",
        validators=[
            dob_not_future,
            MinConsentAgeValidator(settings.MINIMUM_AGE_OF_CONSENT),
            MaxConsentAgeValidator(settings.MAXIMUM_AGE_OF_CONSENT),
        ],
        null=True,
        blank=False,
        help_text="Format is YYYY-MM-DD",
    )

    is_dob_estimated = IsDateEstimatedField(
        verbose_name="Is date of birth estimated?",
        null=True,
        blank=False,
    )

    gender = models.CharField(
        verbose_name="Gender",
        choices=GENDER_UNDETERMINED,
        max_length=1,
        null=True,
        blank=False,
    )

    subject_type = models.CharField(
        max_length=25,
        validators=[SubjectTypeValidator(settings.SUBJECT_TYPES)],
    )

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False,
        help_text='see also edc.data manager.'
    )

    objects = SubjectManager()

    def natural_key(self):
        return (self.subject_identifier_as_pk, )

    class Meta:
        abstract = True
        unique_together = (('subject_identifier', 'identity', 'version'), )
