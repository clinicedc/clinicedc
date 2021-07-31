from django.db import models
from django.utils.html import format_html
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models

from ..choices import CARE_ACCESS
from ..model_mixins import (
    CrfModelMixin,
    DxLocationModelMixin,
    HivArvInitiationModelMixin,
    HivArvMonitoringModelMixin,
    InitialReviewModelMixin,
)


class HivInitialReview(
    HivArvInitiationModelMixin,
    HivArvMonitoringModelMixin,
    InitialReviewModelMixin,
    DxLocationModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):

    receives_care = models.CharField(
        verbose_name="Is the patient receiving care for HIV?",
        max_length=15,
        choices=YES_NO,
    )

    clinic = models.CharField(
        verbose_name="Where does the patient receive care for HIV",
        max_length=15,
        choices=CARE_ACCESS,
        default=NOT_APPLICABLE,
    )

    clinic_other = models.CharField(
        verbose_name=format_html(
            "If <u>not</u> attending here, where does the patient attend?"
        ),
        max_length=50,
        null=True,
        blank=True,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "HIV Initial Review"
        verbose_name_plural = "HIV Initial Reviews"
