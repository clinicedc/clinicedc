from uuid import uuid4

from django.db import models
from django.db.models import PROTECT
from edc_constants.choices import YES_NO
from edc_constants.constants import NO


class PreOrderRefillModelMixin(models.Model):
    # not used
    pre_order_identifier = models.CharField(max_length=36, default=uuid4, editable=False)

    order_or_update_next = models.CharField(
        verbose_name="Order, or update, refill for next scheduled visit?",
        max_length=15,
        choices=YES_NO,
        default=NO,
    )

    # not used
    next_dosage_guideline = models.ForeignKey(
        "edc_pharmacy.DosageGuideline",
        on_delete=PROTECT,
        related_name="next_dosageguideline",
        null=True,
        blank=True,
    )

    # not used
    next_formulation = models.ForeignKey(
        "edc_pharmacy.Formulation",
        on_delete=PROTECT,
        related_name="next_formulation",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Pre-order Refill"
        verbose_name_plural = "Pre-order Refills"
        abstract = True
