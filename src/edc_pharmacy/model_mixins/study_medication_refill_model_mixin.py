from uuid import uuid4

from django.db import models
from django.db.models import PROTECT
from edc_constants.choices import YES_NO
from edc_constants.constants import YES


class StudyMedicationRefillModelMixin(models.Model):
    refill = models.CharField(
        verbose_name="Will the subject receive study medication for this visit",
        max_length=15,
        default=YES,
        choices=YES_NO,
        help_text="If NO, set refill_start_datetime equal to the refill_end_datetime",
    )

    refill_start_datetime = models.DateTimeField()

    refill_end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank to auto-calculate if refilling to the next scheduled visit",
    )

    refill_identifier = models.CharField(max_length=36, default=uuid4, editable=False)

    dosage_guideline = models.ForeignKey(
        "edc_pharmacy.DosageGuideline", on_delete=PROTECT, null=True, blank=False
    )

    formulation = models.ForeignKey(
        "edc_pharmacy.Formulation", on_delete=PROTECT, null=True, blank=False
    )

    roundup_divisible_by = models.IntegerField(default=1)

    refill_to_next_visit = models.CharField(
        verbose_name="Refill to the next scheduled visit",
        max_length=25,
        choices=YES_NO,
        default=YES,
        help_text="If YES, leave refill end date blank to auto-calculate",
    )

    number_of_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Leave blank to auto-calculate relative to the next scheduled appointment",
    )

    special_instructions = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Study Medication"
        verbose_name_plural = "Study Medication"
        abstract = True
