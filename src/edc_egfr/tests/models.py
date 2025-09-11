from clinicedc_tests.models import SubjectRequisition
from django.db import models

from edc_crf.model_mixins import CrfStatusModelMixin
from edc_egfr.model_mixins import EgfrDropNotificationModelMixin, EgfrModelMixin
from edc_lab_panel.panels import rft_panel
from edc_lab_results.model_mixins import BloodResultsMethodsModelMixin
from edc_model.models import BaseUuidModel
from edc_reportable import MICROMOLES_PER_LITER
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_tracking.models import SubjectVisit


class ResultCrf(BloodResultsMethodsModelMixin, EgfrModelMixin, models.Model):
    lab_panel = rft_panel

    egfr_formula_name = "ckd-epi"

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT)

    requisition = models.ForeignKey(SubjectRequisition, on_delete=models.PROTECT)

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


class EgfrDropNotification(
    SiteModelMixin, CrfStatusModelMixin, EgfrDropNotificationModelMixin, BaseUuidModel
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    consent_version = models.CharField(max_length=5, default="1")

    class Meta(EgfrDropNotificationModelMixin.Meta, BaseUuidModel.Meta):
        pass
