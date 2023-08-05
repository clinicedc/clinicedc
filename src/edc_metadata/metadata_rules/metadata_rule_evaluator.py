from __future__ import annotations

from typing import TYPE_CHECKING

from edc_visit_tracking.utils import get_related_visit_model_cls

from .site import site_metadata_rules

if TYPE_CHECKING:
    related_visit_model_cls = get_related_visit_model_cls()


class MetadataRuleEvaluator:

    """Main class to evaluate rules.

    Used by model mixin.
    """

    def __init__(
        self,
        related_visit: related_visit_model_cls = None,
        app_label: str | None = None,
        allow_create: bool | None = None,
    ) -> None:
        self.related_visit = related_visit
        self.app_labels = [app_label] if app_label else []
        self.related_visit_model = related_visit._meta.label_lower
        self.allow_create = allow_create
        if not self.app_labels:
            for rule_groups in site_metadata_rules.registry.values():
                for rule_group in rule_groups:
                    if rule_group._meta.related_visit_model == self.related_visit_model:
                        if rule_group._meta.app_label not in self.app_labels:
                            self.app_labels.append(rule_group._meta.app_label)

    def evaluate_rules(self) -> None:
        for app_label in self.app_labels:
            for rule_group in site_metadata_rules.registry.get(app_label, []):
                rule_group.evaluate_rules(
                    related_visit=self.related_visit, allow_create=self.allow_create
                )
