from edc_crf.model_mixins import CrfModelMixin
from edc_model import models as edc_models

from edc_dx_review.model_mixins import CholInitialReviewModelMixin


class CholInitialReview(
    CholInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(
        CholInitialReviewModelMixin.Meta, CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta
    ):
        pass
