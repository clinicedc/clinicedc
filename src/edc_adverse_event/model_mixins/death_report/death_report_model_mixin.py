from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.deletion import PROTECT
from django.utils import timezone

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
from edc_pdf_reports.model_mixins import PdfReportModelMixin
from edc_protocol.validators import (
    date_not_before_study_start,
    datetime_not_before_study_start,
)
from edc_sites.model_mixins import SiteModelMixin

from ...constants import DEATH_REPORT_ACTION
from ...models import CauseOfDeath
from ...pdf_reports import DeathPdfReport


class DeathReportModelMixin(
    SiteModelMixin,
    UniqueSubjectIdentifierFieldMixin,
    ActionNoManagersModelMixin,
    PdfReportModelMixin,
    models.Model,
):
    action_name = DEATH_REPORT_ACTION

    pdf_report_cls = DeathPdfReport

    death_date_field = "death_datetime"

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=timezone.now,
    )

    death_datetime = models.DateTimeField(
        validators=[datetime_not_before_study_start, datetime_not_future],
        verbose_name="Date and Time of Death",
        null=True,
        blank=False,
    )

    death_date = models.DateField(
        validators=[date_not_before_study_start, date_not_future],
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
        blank=False,
        default="",
    )

    cause_of_death = models.ForeignKey(
        CauseOfDeath,
        on_delete=PROTECT,
        verbose_name="Main cause of death",
        help_text=(
            "Main cause of death in the opinion of the local study doctor and local PI"
        ),
        null=True,
        blank=False,
    )

    cause_of_death_other = OtherCharField(max_length=100, blank=True, default="")

    narrative = models.TextField(verbose_name="Narrative", default="")

    objects = ActionIdentifierModelManager()

    on_site = ActionIdentifierSiteManager()

    history = HistoricalRecords(inherit=True)

    class Meta(
        SiteModelMixin.Meta,
        UniqueSubjectIdentifierFieldMixin.Meta,
        ActionNoManagersModelMixin.Meta,
    ):
        abstract = True
        verbose_name = "Death Report"
        verbose_name_plural = "Death Reports"
        indexes = (
            *ActionNoManagersModelMixin.Meta.indexes,
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"]),
        )

    def natural_key(self):
        return (self.action_identifier,)

    natural_key.dependencies = ("edc_adverse_event.causeofdeath",)
