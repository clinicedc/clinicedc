from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_crf.model_mixins import CrfModelMixin, CrfWithActionModelMixin
from edc_lab.model_mixins import CrfWithRequisitionModelMixin
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_lab_panel.panels import fbc_panel
from edc_model import models as edc_models
from edc_reportable import GRAMS_PER_DECILITER

from edc_lab_results import BLOOD_RESULTS_FBC_ACTION
from edc_lab_results.model_mixins import (
    BloodResultsModelMixin,
    HaemoglobinModelMixin,
    Hba1cModelMixin,
    HctModelMixin,
    PlateletsModelMixin,
    RbcModelMixin,
    WbcModelMixin,
)


class BloodResultsFbc(
    CrfWithActionModelMixin,
    CrfWithRequisitionModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    RbcModelMixin,
    WbcModelMixin,
    PlateletsModelMixin,
    BloodResultsModelMixin,
    edc_models.BaseUuidModel,
):
    action_name = BLOOD_RESULTS_FBC_ACTION

    tracking_identifier_prefix = "FB"

    lab_panel = fbc_panel

    class Meta(CrfWithActionModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Blood Result: FBC"
        verbose_name_plural = "Blood Results: FBC"


class AbcModelMixin(
    reportable_result_model_mixin_factory(
        "hct", ((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),)
    ),
    models.Model,
):
    # HCT
    hct_value = models.DecimalField(
        validators=[MinValueValidator(1.00), MaxValueValidator(999.00)],
        verbose_name="Hematocrit",
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


# this model does not include the requisition and action item mixins
class BloodResultsHba1c(
    CrfModelMixin,
    CrfWithRequisitionModelMixin,
    Hba1cModelMixin,
    BloodResultsModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "HbA1c"
        verbose_name_plural = "HbA1c"
