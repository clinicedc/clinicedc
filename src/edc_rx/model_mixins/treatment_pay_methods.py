from django.core.validators import MinValueValidator
from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import UNKNOWN


class TreatmentPayMethodsModelMixin(models.Model):
    health_insurance = models.CharField(
        verbose_name="Does the patient have any private or work-place health insurance?",
        max_length=15,
        choices=YES_NO,
        default=UNKNOWN,
    )

    health_insurance_monthly_pay = models.IntegerField(
        verbose_name="In the last month, how much has the patient spent on health insurance",
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="amount in local currency",
    )

    patient_club = models.CharField(
        verbose_name="Does the patient belong to a ‘club’ that supports medicines purchase?",
        max_length=15,
        choices=YES_NO,
        default=UNKNOWN,
    )

    patient_club_monthly_pay = models.IntegerField(
        verbose_name="In the last month, how much has the patient spent on club membership",
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="amount in local currency",
    )

    class Meta:
        abstract = True
