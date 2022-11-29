from edc_crf.model_mixins import CrfModelMixin
from edc_model import models as edc_models

from edc_dx_review.model_mixins import HivFollowupReviewModelMixin


class HivReview(HivFollowupReviewModelMixin, CrfModelMixin, edc_models.BaseUuidModel):
    class Meta(
        HivFollowupReviewModelMixin.Meta, CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta
    ):
        verbose_name = "HIV Followup Review"
        verbose_name_plural = "HIV Followup Review"
