from .rule_evaluator import RuleEvaluator


class RequisitionRuleEvaluator(RuleEvaluator):
    def __init__(self, panel=None, **kwargs):
        self.panel = panel
        self.__init__(**kwargs)
