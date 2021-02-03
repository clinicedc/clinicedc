from django.conf import settings
from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE, YES
from edc_model.models import date_not_future
from edc_utils import get_utcnow

from ...choices import AE_GRADE_SIMPLE, AE_OUTCOME


class AeFollowupFieldsModelMixin(models.Model):

    ae_initial = models.ForeignKey(
        f"{settings.ADVERSE_EVENT_APP_LABEL}.aeinitial", on_delete=models.PROTECT
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time", default=get_utcnow
    )

    outcome = models.CharField(blank=False, null=False, max_length=25, choices=AE_OUTCOME)

    outcome_date = models.DateField(validators=[date_not_future])

    ae_grade = models.CharField(
        verbose_name="If severity increased, indicate grade",
        max_length=25,
        choices=AE_GRADE_SIMPLE,
        default=NOT_APPLICABLE,
    )

    relevant_history = models.TextField(
        verbose_name="Description summary of Adverse Event outcome",
        max_length=1000,
        blank=False,
        null=False,
        help_text="Indicate Adverse Event, clinical results,"
        "medications given, dosage,treatment plan and outcomes.",
    )

    followup = models.CharField(
        verbose_name="Is a follow-up to this report required?",
        max_length=15,
        choices=YES_NO,
        default=YES,
        help_text="If NO, this will be considered the final report",
    )

    class Meta:
        abstract = True
