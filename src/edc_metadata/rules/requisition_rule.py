from ..constants import REQUISITION

from .rule import Rule
from collections import OrderedDict


class RequisitionRuleGroupErrror(Exception):
    pass


class RequisitionRule(Rule):

    # rule_evaluator_cls = RequisitionRuleEvaluator

    def __init__(self, target_model, target_panels, **kwargs):
        self.metadata_category = REQUISITION
        self.target_model = target_model
        self.target_panels = target_panels
        for panel in self.target_panels:
            try:
                panel.name
            except AttributeError as e:
                raise RequisitionRuleGroupErrror(
                    f'{e} Expected panel instance. Got panel={panel}.')
        super().__init__(**kwargs)

    def run(self, visit=None):
        """Returns a dictionary of {target_panel: entry_status, ...} updated
        by running the rule for each target panel given a visit.
        """
        result = OrderedDict()
        rule_evaluator = self.rule_evaluator_cls(
            logic=self.logic, source_model=self.source_model, visit=visit)
        entry_status = rule_evaluator.result
        for target_panel in self.target_panels:
            result.update({target_panel: entry_status})
        return result
