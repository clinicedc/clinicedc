from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE

from ...choices import CHOL_MANAGEMENT
from ..dx_location_model_mixin import DxLocationModelMixin
from .ncd_initial_review_model_mixin import NcdInitialReviewModelMixin


class CholInitialReviewModelMixin(
    DxLocationModelMixin,
    NcdInitialReviewModelMixin,
):
    ncd_condition_label = "cholesterol"

    managed_by = models.CharField(
        verbose_name="How is the patient's cholesterol managed?",
        max_length=25,
        choices=CHOL_MANAGEMENT,
        default=NOT_APPLICABLE,
    )

    chol_performed = models.CharField(
        verbose_name=(
            "Has the patient had their cholesterol measured in the last few months?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    class Meta:
        abstract = True
        verbose_name = "High Cholesterol Initial Review"
        verbose_name_plural = "High Cholesterol Initial Reviews"
