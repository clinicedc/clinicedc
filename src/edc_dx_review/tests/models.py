from edc_blood_results import BLOOD_RESULTS_FBC_ACTION
from edc_blood_results.model_mixins import (
    BloodResultsModelMixin,
    HaemoglobinModelMixin,
    HctModelMixin,
    PlateletsModelMixin,
    RbcModelMixin,
    RequisitionModelMixin,
    WbcModelMixin,
)
from edc_crf.crf_with_action_model_mixin import CrfWithActionModelMixin
from edc_model import models as edc_models


class BloodResultsFbc(
    CrfWithActionModelMixin,
    RequisitionModelMixin,
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

    class Meta(CrfWithActionModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Blood Result: FBC"
        verbose_name_plural = "Blood Results: FBC"
