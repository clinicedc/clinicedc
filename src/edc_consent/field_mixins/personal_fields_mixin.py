from django.core.validators import RegexValidator
from django.db import models
from django.utils.html import format_html
from django_crypto_fields.fields import (
    EncryptedCharField,
    FirstnameField,
    LastnameField,
)
from django_crypto_fields.models import CryptoMixin
from edc_constants.choices import GENDER_UNDETERMINED
from edc_model.models import NameFieldsModelMixin
from edc_model_fields.fields import IsDateEstimatedField

from ..validators import FullNameValidator


class BaseFieldsMixin(models.Model):
    dob = models.DateField(verbose_name="Date of birth", null=True, blank=False)

    is_dob_estimated = IsDateEstimatedField(
        verbose_name="Is date of birth estimated?", null=True, blank=False
    )

    gender = models.CharField(
        verbose_name="Gender",
        choices=GENDER_UNDETERMINED,
        max_length=1,
        null=True,
        blank=False,
    )

    guardian_name = LastnameField(
        verbose_name="Guardian's last and first name",
        validators=[FullNameValidator()],
        blank=True,
        null=True,
        help_text=format_html(
            "Required only if participant is a minor.<BR>"
            "Format is 'LASTNAME, FIRSTNAME'. "
            "All uppercase separated by a comma."
        ),
    )

    subject_type = models.CharField(max_length=25)

    class Meta:
        abstract = True


class FullNamePersonalFieldsMixin(
    CryptoMixin, NameFieldsModelMixin, BaseFieldsMixin, models.Model
):
    class Meta:
        abstract = True


class PersonalFieldsMixin(CryptoMixin, BaseFieldsMixin, models.Model):
    first_name = FirstnameField(
        null=True,
        blank=False,
        validators=[
            RegexValidator(
                regex=r"^([A-Z]+$|[A-Z]+\ [A-Z]+)$",
                message="Ensure name consist of letters only in upper case",
            )
        ],
        help_text="Use UPPERCASE letters only.",
    )

    last_name = LastnameField(
        verbose_name="Surname",
        null=True,
        blank=False,
        validators=[
            RegexValidator(
                regex=r"^([A-Z]+$|[A-Z]+\ [A-Z]+)$",
                message="Ensure name consist of letters only in upper case",
            )
        ],
        help_text="Use UPPERCASE letters only.",
    )

    initials = EncryptedCharField(
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2,3}$",
                message="Ensure initials consist of letters only in upper case, no spaces.",
            )
        ],
        null=True,
        blank=False,
    )

    class Meta:
        abstract = True
