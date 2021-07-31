from edc_crf.crf_model_mixin import CrfModelMixin as BaseCrfModelMixin
from edc_crf.crf_status_model_mixin import CrfStatusModelMixin


class CrfModelMixin(CrfStatusModelMixin, BaseCrfModelMixin):
    class Meta(BaseCrfModelMixin.Meta):
        abstract = True
