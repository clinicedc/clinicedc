from edc_metadata.constants import REQUISITION

from ..rule import Rule
from ..rule_evaluator import RuleEvaluator


class RequisitionRuleEvaluatorError(Exception):
    pass


class RequisitionRuleEvaluator(RuleEvaluator):

    def __init__(self, source_panel=None, **kwargs):
        self.source_panel = source_panel
        super().__init__(**kwargs)


class RequisitionRule(Rule):

    rule_evaluator_cls = RequisitionRuleEvaluator

    def __init__(self, source_panel=None, target_panels=None, **kwargs):
        self.metadata_category = REQUISITION
        try:
            self.target_panels = [p.name for p in target_panels]
        except AttributeError:
            self.target_panels = target_panels
        try:
            self.source_panel = source_panel.name
        except AttributeError:
            self.source_panel = source_panel
        super().__init__(**kwargs)
