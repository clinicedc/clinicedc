from django.db import models
from django.db.models import PROTECT
from edc_appointment_app.models import SubjectVisit
from edc_crf.model_mixins import CrfStatusModelMixin
from edc_lab.model_mixins import CrfWithRequisitionModelMixin, requisition_fk_options
from edc_lab_panel.panels import fbc_panel
from edc_lab_results.model_mixins import (
    BloodResultsModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    MchcModelMixin,
    MchModelMixin,
    McvModelMixin,
    PlateletsModelMixin,
    RbcModelMixin,
    WbcModelMixin,
)
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin

requisition_fk_options.update(to="edc_appointment_app.SubjectRequisition")


class BloodResultsFbc(
    SiteModelMixin,
    CrfWithRequisitionModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    RbcModelMixin,
    WbcModelMixin,
    PlateletsModelMixin,
    MchModelMixin,
    MchcModelMixin,
    McvModelMixin,
    BloodResultsModelMixin,
    CrfStatusModelMixin,
    BaseUuidModel,
):
    lab_panel = fbc_panel

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    requisition = models.ForeignKey(
        limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
    )

    def get_summary(self):
        return ""

    class Meta(CrfStatusModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Blood Result: FBC"
        verbose_name_plural = "Blood Results: FBC"
