from django.db import models
from edc_constants.constants import NOT_APPLICABLE

from ...choices import CHOL_MANAGEMENT
from .followup_review_model_mixin import FollowupReviewModelMixin


class CholReviewModelMixin(FollowupReviewModelMixin):

    managed_by = models.CharField(
        verbose_name="How will the patient's High Cholesterol be managed going forward?",
        max_length=25,
        choices=CHOL_MANAGEMENT,
        default=NOT_APPLICABLE,
    )

    class Meta(FollowupReviewModelMixin.Meta):
        verbose_name = "High Cholesterol Review"
        verbose_name_plural = "High Cholesterol Review"
