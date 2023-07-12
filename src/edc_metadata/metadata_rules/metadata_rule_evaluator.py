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
        self.app_label = app_label or related_visit._meta.app_label
        self.allow_create = allow_create

    def evaluate_rules(self) -> None:
        for rule_group in site_metadata_rules.registry.get(self.app_label, []):
            rule_group.evaluate_rules(
                related_visit=self.related_visit, allow_create=self.allow_create
            )
