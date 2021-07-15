from django.db import models
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models

from ..choices import DM_MANAGEMENT
from ..model_mixins import (
    CrfModelMixin,
    DxLocationModelMixin,
    InitialReviewModelMixin,
    NcdInitialReviewModelMixin,
)


class DmInitialReview(
    InitialReviewModelMixin,
    DxLocationModelMixin,
    NcdInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):

    ncd_condition_label = "diabetes"

    managed_by = models.CharField(
        verbose_name="How is the patient's diabetes managed?",
        max_length=25,
        choices=DM_MANAGEMENT,
        default=NOT_APPLICABLE,
        help_text="If insulin or oral drugs, diet and lifestyle is assumed.",
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Diabetes Initial Review"
        verbose_name_plural = "Diabetes Initial Reviews"
