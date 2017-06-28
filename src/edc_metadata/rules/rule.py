from collections import OrderedDict

from .rule_evaluator import RuleEvaluator


class RuleError(Exception):
    pass


class Rule:

    rule_evaluator_cls = RuleEvaluator

    def __init__(self, logic=None):
        self.logic = logic
        self.target_models = None
        self.app_label = None  # set by metaclass
        self.group = None  # set by metaclass
        self.name = None  # set by metaclass
        self.source_model = None  # set by metaclass

    def __repr__(self):
        return (f'{self.__class__.__name__}(name=\'{self.name}\', group=\'{self.group}\')')

    def __str__(self):
        return f'{self.group}.{self.name}'

    def run(self, visit=None):
        """Returns a dictionary of {target_model: entry_status, ...} updated
        by running the rule for each target model given a visit.
        """
        result = OrderedDict()
        rule_evaluator = self.rule_evaluator_cls(
            logic=self.logic, source_model=self.source_model, visit=visit)
        entry_status = rule_evaluator.result
        for target_model in self.target_models:
            result.update({target_model: entry_status})
        return result
