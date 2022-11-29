from edc_crf.model_mixins import CrfModelMixin
from edc_model import models as edc_models

from edc_dx_review.model_mixins import (
    ClinicalReviewCholModelMixin,
    ClinicalReviewDmModelMixin,
    ClinicalReviewHivModelMixin,
    ClinicalReviewHtnModelMixin,
    ClinicalReviewModelMixin,
)


class ClinicalReview(
    ClinicalReviewHivModelMixin,
    ClinicalReviewHtnModelMixin,
    ClinicalReviewDmModelMixin,
    ClinicalReviewCholModelMixin,
    ClinicalReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Clinical Review"
        verbose_name_plural = "Clinical Review"
