from edc_metadata.constants import REQUISITION

from ..rule import Rule


class RequisitionRule(Rule):

    def __init__(self, target_model=None, target_panels=None, **kwargs):
        super().__init__(**kwargs)
        self.metadata_category = REQUISITION
        self.target_models = [target_model]
        try:
            self.target_panels = [p.name for p in target_panels]
        except AttributeError:
            self.target_panels = target_panels
