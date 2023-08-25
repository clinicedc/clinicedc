from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.html import format_html
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_model import models as edc_models

from .choices import MISSED_PILLS


class MedicationAdherenceModelMixin(models.Model):
    visual_score_slider = models.CharField(
        verbose_name="Visual score", max_length=3, help_text="%"
    )

    visual_score_confirmed = models.IntegerField(
        verbose_name=format_html(
            "<B><font color='orange'>Interviewer</font></B>: "
            "please transcribe the score indicated from above."
        ),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="%",
    )

    last_missed_pill = models.CharField(
        verbose_name="When was the last time you missed your study pill?",
        max_length=25,
        choices=MISSED_PILLS,
    )

    pill_count_performed = models.CharField(
        verbose_name="Was a pill count performed", max_length=5, choices=YES_NO, default=YES
    )

    pill_count_not_performed_reason = models.TextField(
        verbose_name="If not performed, please explain ...",
        null=True,
        blank=True,
    )

    pill_count = models.IntegerField(
        verbose_name="Number of pills left in the bottle", null=True, blank=True
    )

    missed_pill_reason = models.ManyToManyField(
        f"{settings.LIST_MODEL_APP_LABEL}.NonAdherenceReasons",
        verbose_name="Reasons for missing study pills",
        blank=True,
    )

    other_missed_pill_reason = edc_models.OtherCharField(max_length=150)

    class Meta:
        abstract = True
        verbose_name = "Medication Adherence"
        verbose_name_plural = "Medication Adherence"
