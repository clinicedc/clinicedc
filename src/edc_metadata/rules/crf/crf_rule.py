from edc_metadata.constants import CRF

from ..rule import Rule


class CrfRule(Rule):

    def __init__(self, target_models=None, **kwargs):
        super().__init__(**kwargs)
        self.metadata_category = CRF
        self.target_models = target_models
