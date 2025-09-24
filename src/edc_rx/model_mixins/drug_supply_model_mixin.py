from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class DrugSupplyModelMixin(models.Model):
    clinic_days = models.IntegerField(
        verbose_name="Clinic",
        validators=[MinValueValidator(0), MaxValueValidator(180)],
        help_text="days",
    )

    club_days = models.IntegerField(
        verbose_name="Club",
        validators=[MinValueValidator(0), MaxValueValidator(180)],
        help_text="days",
    )

    purchased_days = models.IntegerField(
        verbose_name="To purchase",
        validators=[MinValueValidator(0), MaxValueValidator(180)],
        help_text=(
            "This can be purchased by patient, through a medicines club "
            "that the patient belong to, through insurance or someone else has paid. "
        ),
    )

    class Meta:
        abstract = True
