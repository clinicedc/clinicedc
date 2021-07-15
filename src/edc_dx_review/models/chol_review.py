from edc_model import models as edc_models

from ..model_mixins import CholReviewModelMixin, CrfModelMixin


class CholReview(CholReviewModelMixin, CrfModelMixin, edc_models.BaseUuidModel):
    class Meta(CholReviewModelMixin.Meta, CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        pass
