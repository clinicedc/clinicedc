from edc_model import models as edc_models

from ..model_mixins import (
    ClinicalReviewBaselineCholModelMixin,
    ClinicalReviewBaselineDmModelMixin,
    ClinicalReviewBaselineHivModelMixin,
    ClinicalReviewBaselineHtnModelMixin,
    ClinicalReviewBaselineModelMixin,
    CrfModelMixin,
)


class ClinicalReviewBaseline(
    ClinicalReviewBaselineHivModelMixin,
    ClinicalReviewBaselineHtnModelMixin,
    ClinicalReviewBaselineDmModelMixin,
    ClinicalReviewBaselineCholModelMixin,
    ClinicalReviewBaselineModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Clinical Review: Baseline"
        verbose_name_plural = "Clinical Review: Baseline"
