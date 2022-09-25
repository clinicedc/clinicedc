from django.db import models
from django.db.models import PROTECT
from edc_constants.choices import GENDER
from edc_lab.model_mixins import PanelModelMixin
from edc_lab_panel.panels import rft_panel
from edc_lab_results.model_mixins import BloodResultsMethodsModelMixin
from edc_model.models import BaseUuidModel
from edc_reportable import MICROMOLES_PER_LITER
from edc_screening.model_mixins import ScreeningIdentifierModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from edc_egfr.model_mixins import EgfrDropNotificationModelMixin, EgfrModelMixin


class SubjectScreening(ScreeningIdentifierModelMixin, BaseUuidModel):
    screening_identifier = models.CharField(
        verbose_name="Screening ID",
        max_length=50,
        blank=True,
        unique=True,
        editable=False,
    )

    gender = models.CharField(choices=GENDER, max_length=10)

    age_in_years = models.IntegerField()

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )


class Appointment(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    appt_datetime = models.DateTimeField(
        verbose_name="Appointment date and time", db_index=True
    )

    timepoint = models.IntegerField(default=0)

    visit_code_sequence = models.IntegerField(default=0)

    visit_schedule_name = models.CharField(max_length=25, default="visit_schedule")

    schedule_name = models.CharField(max_length=25, default="schedule")

    class Meta(BaseUuidModel.Meta):
        pass


class SubjectVisit(SiteModelMixin, BaseUuidModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=PROTECT,
    )

    subject_identifier = models.CharField(max_length=25, null=True)

    consent_version = models.CharField(max_length=5, default="1")

    report_datetime = models.DateTimeField()

    visit_code_sequence = models.IntegerField(default=0)

    visit_schedule_name = models.CharField(max_length=25, default="visit_schedule")

    schedule_name = models.CharField(max_length=25, default="schedule")

    class Meta(BaseUuidModel.Meta):
        app_label = "egfr_app"


class SubjectRequisition(PanelModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )

    requisition_datetime = models.DateTimeField(
        default=get_utcnow,
        verbose_name="Requisition Date",
    )

    class Meta:
        pass


class ResultCrf(BloodResultsMethodsModelMixin, EgfrModelMixin, models.Model):
    lab_panel = rft_panel

    egfr_formula_name = "ckd-epi"

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    requisition = models.ForeignKey(SubjectRequisition, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )

    assay_datetime = models.DateTimeField(default=get_utcnow())

    creatinine_value = models.DecimalField(
        decimal_places=2, max_digits=6, null=True, blank=True
    )

    creatinine_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MICROMOLES_PER_LITER, MICROMOLES_PER_LITER),),
        null=True,
        blank=True,
    )

    @property
    def related_visit(self):
        return self.subject_visit


class EgfrDropNotification(SiteModelMixin, EgfrDropNotificationModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    consent_version = models.CharField(max_length=5, default="1")

    class Meta(EgfrDropNotificationModelMixin.Meta, BaseUuidModel.Meta):
        app_label = "egfr_app"
