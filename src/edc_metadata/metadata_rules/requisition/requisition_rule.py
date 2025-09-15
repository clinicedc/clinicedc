from typing import Any

from ...constants import REQUISITION
from ..rule import Rule
from ..rule_evaluator import RuleEvaluator


class RequisitionRuleEvaluatorError(Exception):
    pass


class RequisitionRuleEvaluator(RuleEvaluator):
    def __init__(self, source_panel: Any | None = None, **kwargs) -> None:
        self.source_panel = source_panel
        super().__init__(**kwargs)


class RequisitionRule(Rule):
    rule_evaluator_cls = RequisitionRuleEvaluator

    def __init__(
        self,
        source_panel: Any | None = None,
        target_panels: list | None = None,
        **kwargs,
    ) -> None:
        self.metadata_category = REQUISITION
        self.target_panels = [p for p in target_panels]
        self.source_panel = source_panel
        super().__init__(**kwargs)
