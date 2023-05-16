from django.db import models
from edc_constants.choices import YES_NO
from edc_model.validators import datetime_not_future
from edc_utils import get_utcnow

from ..choices import DEVIATION_VIOLATION, REPORT_STATUS
from ..models import ActionsRequired, ProtocolViolations


class ProtocolIncidentModelMixin(models.Model):
    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    short_description = models.CharField(
        verbose_name="Provide a short description of this incident",
        max_length=35,
        null=True,
        blank=False,
        help_text=(
            (
                "Max 35 characters. Note: there is additional space below for "
                "a more detailed description"
            )
        ),
    )

    report_type = models.CharField(
        verbose_name="Type of incident", max_length=25, choices=DEVIATION_VIOLATION
    )

    safety_impact = models.CharField(
        verbose_name="Could this incident have an impact on safety of the participant?",
        max_length=25,
        choices=YES_NO,
    )

    safety_impact_details = models.TextField(
        verbose_name='If "Yes", provide details', null=True, blank=True
    )

    study_outcomes_impact = models.CharField(
        verbose_name="Could this incident have an impact on study outcomes?",
        max_length=25,
        choices=YES_NO,
    )

    study_outcomes_impact_details = models.TextField(
        verbose_name='If "Yes", provide details', null=True, blank=True
    )

    incident_datetime = models.DateTimeField(
        verbose_name="Date incident occurred",
        validators=[datetime_not_future],
        null=True,
        blank=False,
    )

    incident = models.ForeignKey(
        ProtocolViolations,
        verbose_name="Type of incident",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="+",
    )

    incident_other = models.CharField(
        null=True, blank=True, verbose_name="If other, please specify", max_length=75
    )

    incident_description = models.TextField(
        verbose_name="Describe the incident",
        null=True,
        blank=False,
        help_text="Describe in full. Explain how the incident happened, what occurred, etc.",
    )

    incident_reason = models.TextField(
        verbose_name="Explain the reason why the incident occurred",
        null=True,
        blank=False,
    )

    corrective_action_datetime = models.DateTimeField(
        verbose_name="Corrective action date and time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    corrective_action = models.TextField(
        verbose_name="Corrective action taken", null=True, blank=True
    )

    preventative_action_datetime = models.DateTimeField(
        verbose_name="Preventative action date and time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    preventative_action = models.TextField(
        verbose_name="Preventative action taken", null=True, blank=True
    )

    action_required = models.ForeignKey(
        ActionsRequired,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    report_status = models.CharField(
        verbose_name="What is the status of this report?",
        max_length=25,
        choices=REPORT_STATUS,
    )

    reasons_withdrawn = models.TextField(null=True, blank=True)

    report_closed_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time report closed.",
    )

    class Meta:
        abstract = True
        verbose_name = "Protocol Incident"
        verbose_name_plural = "Protocol Incident"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
