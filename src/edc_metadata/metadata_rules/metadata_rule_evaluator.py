from typing import Any, Optional

from .site import site_metadata_rules


class MetadataRuleEvaluator:

    """Main class to evaluate rules.

    Used by model mixin.
    """

    def __init__(
        self, visit_model_instance: Optional[Any] = None, app_label: Optional[str] = None
    ) -> None:
        self.visit_model_instance = visit_model_instance
        self.app_label = app_label or visit_model_instance._meta.app_label

    def evaluate_rules(self) -> None:
        for rule_group in site_metadata_rules.registry.get(self.app_label, []):
            rule_group.evaluate_rules(visit=self.visit_model_instance)
