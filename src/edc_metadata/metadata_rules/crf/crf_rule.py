from __future__ import annotations

from typing import TYPE_CHECKING

from ...constants import CRF
from ..rule import Rule

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ...model_mixins.creates import CreatesMetadataModelMixin

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass


class CrfRuleModelConflict(Exception):
    pass


class CrfRule(Rule):
    def __init__(self, target_models: list[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.metadata_category = CRF
        self.target_models = target_models

    def run(self, related_visit: RelatedVisitModel = None) -> dict[str, str]:
        if self.source_model in self.target_models:
            raise CrfRuleModelConflict(
                f"Source model cannot be a target model. Got '{self.source_model}' "
                f"is in target models {self.target_models}"
            )
        return super().run(related_visit=related_visit)
