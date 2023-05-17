from typing import Any, Optional

from ...constants import REQUISITION
from ..rule import Rule
from ..rule_evaluator import RuleEvaluator


class RequisitionRuleEvaluatorError(Exception):
    pass


class RequisitionRuleEvaluator(RuleEvaluator):
    def __init__(self, source_panel: Optional[Any] = None, **kwargs) -> None:
        self.source_panel = source_panel
        super().__init__(**kwargs)


class RequisitionRule(Rule):
    rule_evaluator_cls = RequisitionRuleEvaluator

    def __init__(
        self,
        source_panel: Optional[Any] = None,
        target_panels: Optional[list] = None,
        **kwargs,
    ) -> None:
        self.metadata_category = REQUISITION
        self.target_panels = [p for p in target_panels]
        self.source_panel = source_panel
        super().__init__(**kwargs)
