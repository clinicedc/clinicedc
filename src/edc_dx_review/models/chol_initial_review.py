from edc_model import models as edc_models

from ..model_mixins import CholInitialReviewModelMixin, CrfModelMixin


class CholInitialReview(
    CholInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    class Meta(
        CholInitialReviewModelMixin.Meta, CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta
    ):
        pass
