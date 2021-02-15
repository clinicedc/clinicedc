from collections import OrderedDict

from .logic import Logic
from .rule_evaluator import RuleEvaluator


class RuleError(Exception):
    pass


class Rule:

    rule_evaluator_cls = RuleEvaluator
    logic_cls = Logic

    def __init__(self, predicate=None, consequence=None, alternative=None):
        self._logic = self.logic_cls(
            predicate=predicate, consequence=consequence, alternative=alternative
        )
        self.target_models = None
        self.app_label = None  # set by metaclass
        self.group = None  # set by metaclass
        self.name = None  # set by metaclass
        self.source_model = None  # set by metaclass
        self.reference_getter_cls = None  # set by metaclass
        self.field_names = []
        try:
            self.field_names = [predicate.attr]
        except AttributeError:
            try:
                self.field_names = predicate.attrs
            except AttributeError:
                pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', group='{self.group}')"

    def __str__(self):
        return f"{self.group}.{self.name}"

    def run(self, visit=None):
        """Returns a dictionary of {target_model: entry_status, ...} updated
        by running the rule for each target model given a visit.

        Ensure the model.field is registered with `site_reference_configs`.
        See `edc_reference`.
        """
        result = OrderedDict()
        opts = {k: v for k, v in self.__dict__.items() if k.startswith != "_"}
        rule_evaluator = self.rule_evaluator_cls(visit=visit, logic=self._logic, **opts)
        entry_status = rule_evaluator.result
        for target_model in self.target_models:
            result.update({target_model: entry_status})
        return result
