from django.core.validators import RegexValidator
from django.db import models
from django_crypto_fields.fields import (
    FirstnameField, LastnameField, EncryptedCharField)
from django_crypto_fields.mixins import CryptoMixin

from edc_base.model_fields import IsDateEstimatedField
from edc_constants.choices import GENDER_UNDETERMINED

from ..validators import FullNameValidator


class PersonalFieldsMixin(CryptoMixin, models.Model):

    first_name = FirstnameField(
        null=True,
    )

    last_name = LastnameField(
        verbose_name="Last name",
        null=True,
    )

    initials = EncryptedCharField(
        validators=[RegexValidator(
            regex=r'^[A-Z]{2,3}$',
            message=('Ensure initials consist of letters '
                     'only in upper case, no spaces.')), ],
        null=True,
    )

    dob = models.DateField(
        verbose_name="Date of birth",
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
        blank=False)

    guardian_name = LastnameField(
        verbose_name=("Guardian\'s Last and first name (minors only)"),
        validators=[FullNameValidator()],
        blank=True,
        null=True,
        help_text=(
            'Required only if subject is a minor. Format is \'LASTNAME, FIRSTNAME\'. '
            'All uppercase separated by a comma then followe by a space.'))

    subject_type = models.CharField(
        max_length=25)

    class Meta:
        abstract = True
