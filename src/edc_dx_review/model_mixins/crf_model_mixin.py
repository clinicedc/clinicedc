from edc_crf.model_mixins import CrfModelMixin as BaseCrfModelMixin
from edc_crf.model_mixins import CrfStatusModelMixin


class CrfModelMixin(CrfStatusModelMixin, BaseCrfModelMixin):
    class Meta(BaseCrfModelMixin.Meta):
        abstract = True
