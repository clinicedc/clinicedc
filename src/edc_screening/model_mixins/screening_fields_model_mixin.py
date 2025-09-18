from uuid import uuid4

from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.utils import timezone
from django_crypto_fields.fields import EncryptedCharField

from edc_constants.choices import GENDER, YES_NO, YES_NO_NA
from edc_constants.constants import NO, NOT_APPLICABLE
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.model_mixins import SiteModelMixin


class ScreeningFieldsModeMixin(SiteModelMixin, models.Model):
    reference = models.UUIDField(
        verbose_name="Reference", unique=True, default=uuid4, editable=False
    )

    screening_identifier = models.CharField(
        verbose_name="Screening ID",
        max_length=50,
        blank=True,
        unique=True,
        editable=False,
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=timezone.now,
        help_text="Date and time of report.",
    )

    initials = EncryptedCharField(
        validators=[
            RegexValidator("[A-Z]{1,3}", "Invalid format"),
            MinLengthValidator(2),
            MaxLengthValidator(3),
        ],
        help_text="Use UPPERCASE letters only. May be 2 or 3 letters.",
        blank=False,
    )

    gender = models.CharField(choices=GENDER, max_length=10)

    age_in_years = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(110)]
    )

    ethnicity = models.CharField(max_length=25, default="", blank=True)

    consent_ability = models.CharField(
        verbose_name="Participant or legal guardian/representative able and "
        "willing to give informed consent.",
        max_length=25,
        choices=YES_NO,
    )

    unsuitable_for_study = models.CharField(
        verbose_name=(
            "Is there any other reason the patient is deemed to not be suitable for the study?"
        ),
        max_length=5,
        choices=YES_NO,
        default=NO,
        help_text="If YES, patient NOT eligible, please give reason below.",
    )

    reasons_unsuitable = models.TextField(
        verbose_name="Reason not suitable for the study",
        max_length=150,
        default="",
        blank=True,
    )

    unsuitable_agreed = models.CharField(
        verbose_name=(
            "Does the study coordinator agree that the patient is not suitable for the study?"
        ),
        max_length=5,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    consented = models.BooleanField(default=False, editable=False)

    refused = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True
