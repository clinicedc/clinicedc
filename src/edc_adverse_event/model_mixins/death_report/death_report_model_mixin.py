from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.managers import (
    ActionIdentifierModelManager,
    ActionIdentifierSiteManager,
)
from edc_action_item.models import ActionNoManagersModelMixin
from edc_constants.choices import YES_NO
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import HistoricalRecords
from edc_model.validators import date_not_future, datetime_not_future
from edc_model_fields.fields.other_charfield import OtherCharField
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from ...constants import DEATH_REPORT_ACTION
from ...models import CauseOfDeath
from ...pdf_reports import DeathPdfReport


class DeathReportModelMixin(
    SiteModelMixin,
    UniqueSubjectIdentifierFieldMixin,
    ActionNoManagersModelMixin,
    models.Model,
):
    action_name = DEATH_REPORT_ACTION

    pdf_report_cls = DeathPdfReport

    death_date_field = "death_datetime"

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    death_datetime = models.DateTimeField(
        validators=[datetime_not_future],
        verbose_name="Date and Time of Death",
        null=True,
        blank=False,
    )

    death_date = models.DateField(
        validators=[date_not_future],
        verbose_name="Date of Death",
        null=True,
        blank=False,
    )

    study_day = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Study day",
        null=True,
        blank=False,
    )

    death_as_inpatient = models.CharField(
        choices=YES_NO,
        max_length=5,
        verbose_name="Death as inpatient",
        null=True,
        blank=False,
    )

    cause_of_death = models.ForeignKey(
        CauseOfDeath,
        on_delete=PROTECT,
        verbose_name="Main cause of death",
        help_text=(
            "Main cause of death in the opinion of the " "local study doctor and local PI"
        ),
        null=True,
        blank=False,
    )

    cause_of_death_other = OtherCharField(max_length=100, blank=True, null=True)

    narrative = models.TextField(verbose_name="Narrative", blank=False, null=True)

    objects = ActionIdentifierModelManager()

    on_site = ActionIdentifierSiteManager()

    history = HistoricalRecords(inherit=True)

    def natural_key(self):
        return (self.action_identifier,)  # noqa

    natural_key.dependencies = ["edc_adverse_event.causeofdeath"]

    class Meta:
        abstract = True
        verbose_name = "Death Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
