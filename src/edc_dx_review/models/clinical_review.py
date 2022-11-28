from edc_model import models as edc_models

from ..model_mixins import (
    ClinicalReviewCholModelMixin,
    ClinicalReviewDmModelMixin,
    ClinicalReviewHivModelMixin,
    ClinicalReviewHtnModelMixin,
    ClinicalReviewModelMixin,
    CrfModelMixin,
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
