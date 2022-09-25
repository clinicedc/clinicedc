from typing import Any, Optional

from .site import site_metadata_rules


class MetadataRuleEvaluator:

    """Main class to evaluate rules.

    Used by model mixin.
    """

    def __init__(
        self, related_visit: Optional[Any] = None, app_label: Optional[str] = None
    ) -> None:
        self.related_visit = related_visit
        self.app_label = app_label or related_visit._meta.app_label

    def evaluate_rules(self) -> None:
        for rule_group in site_metadata_rules.registry.get(self.app_label, []):
            rule_group.evaluate_rules(visit=self.related_visit)
